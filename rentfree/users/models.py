import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager

class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = None
    user_name = models.CharField(
        _('user_name'),
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        help_text=_('15 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that user name already exists.'),
        },
    )
    email = models.EmailField(_('email address'), unique=True)
    is_mailsubscribed = models.BooleanField(default=True)
    is_paysubscribed = models.PositiveSmallIntegerField(default=0)
    paysubscribe_changed = models.DateTimeField(default=timezone.now, blank=True)
    is_smssubscribed = models.BooleanField(default=False)
    is_newuserprofile = models.BooleanField(default=True)
    stripe_customer = models.ForeignKey(
        'djstripe.Customer', null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_('The user Stripe Customer object, if it exists.')
    )
    stripe_subscription = models.ForeignKey(
        'djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_('The user Stripe Subscription object, if it exists.')
    )
    stripe_paymentmethod = models.ForeignKey(
        'djstripe.PaymentMethod', null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_('The user Stripe Payment Method object, if it exists.')
        )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    url = models.URLField(null=True, blank=True,
        help_text=_('The preferred url for this user, will be linked on content pages for their bio.')
        )
    download_resets = models.SmallIntegerField(_('Download resets'), blank=False, null=False, default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class CustomUserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='base_userprofile'
    )
    phone = PhoneNumberField(_('phone number'), blank=True, unique=True, default=None, null=True)


    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users_customuser_profile'

    def __str__(self):
        return self.user.email
