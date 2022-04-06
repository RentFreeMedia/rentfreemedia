import pathlib
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from io import BytesIO
from wagtail.users.models import UserProfile
from custom_storages import s3_media_storage
from users.models import CustomUserProfile, CustomUser
from PIL import Image


@receiver(user_signed_up)
def group_and_profiles(sender, request, user, **kwargs):
	""" add new user to "customers" group, create
	wagtail and user profile fields with a default
	language setting. """
	if user.is_anonymous:
		pass
	else:
		group = Group.objects.get(name='Customers')
		user.groups.add(group)
		wagtail_userprofile_defaults = {
			'submitted_notifications': False,
			'approved_notifications': False,
			'rejected_notifications': False,
			'preferred_language': 'en',
		}

		base_userprofile_defaults = {
			'user_id': user.id,
		}
		user.save()
		UserProfile.objects.get_or_create(user_id=user.id, defaults=wagtail_userprofile_defaults)
		CustomUserProfile.objects.get_or_create(user_id=user.id, defaults=base_userprofile_defaults)


@receiver(post_save, sender=CustomUser)
def default_groups(sender, instance, **kwargs):
	if instance.is_superuser and kwargs.get('created'):
		Group.objects.get_or_create(name='Contributors')
		Group.objects.get_or_create(name='Authors')
		Group.objects.get_or_create(name='Customers')
		user = CustomUser.objects.get(pk=instance.id)
		groups = Group.objects.all()
		user.first_name = 'Admin'
		user.last_name = 'McAdmin'
		user.is_smssubscribed = True
		user.is_mailsubscribed = True
		user.is_active = True
		for group in groups:
			group.user_set.add(user)
		user.save()

		wagtail_userprofile_defaults = {
			'submitted_notifications': True,
			'approved_notifications': True,
			'rejected_notifications': True,
			'updated_comments_notifications': True,
			'preferred_language': 'en',
		}

		base_userprofile_defaults = {
			'user_id': user.id,
		}

		UserProfile.objects.get_or_create(user_id=user.id, defaults=wagtail_userprofile_defaults)
		CustomUserProfile.objects.get_or_create(user_id=user.id, defaults=base_userprofile_defaults)
	else:
		pass


def crop_center(img, crop_width, crop_height):
	width, height = img.size
	return img.crop(((width - crop_width) // 2,
					(height - crop_height) // 2,
					(width + crop_width) // 2,
					(height + crop_height) // 2))


def crop_max_square(img):
    return crop_center(img, min(img.size), min(img.size))



@receiver(post_save, sender=UserProfile)
def resize_avatar(sender, instance, **kwargs):
	if instance.avatar:
		memfile = BytesIO()
		try:
			img = Image.open(instance.avatar.file)
		except:
			img = None

		if img:
			width, height = img.size
			newsize = 100, 100
			try:
				imgformat = img.format
			except:
				imgformat = pathlib.Path(instance.avatar.file.name).suffix.split('.')[1].upper()
			img = crop_max_square(img).resize((newsize), Image.LANCZOS)
			img.save(memfile, imgformat)
			s3_media_storage.save(instance.avatar.name, memfile)
			img.close()
			memfile.close()
