from custom_storages import s3_priv_storage
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import CustomUserProfile
from wagtailmedia.models import AbstractMedia
from website.utils import slugify_filename

class CustomMedia(AbstractMedia):

    file = models.FileField(upload_to=slugify_filename, storage=s3_priv_storage, verbose_name=_('file'))
    thumbnail = models.FileField(upload_to='media_thumbnails', blank=True, verbose_name=_('thumbnail')
    )

    duration = models.CharField(
        blank=False,
        null=False,
        verbose_name=_('duration'),
        max_length=25,
        help_text=_('Duration in seconds. Valid input formats: HH:MM:SS, MM:SS, or SS.'),
    )

    downloads = models.ManyToManyField(CustomUserProfile, related_name='media_download', through='Download')

    admin_form_fields = (
        "title",
        "file",
        "collection",
        "duration",
        "width",
        "height",
        "thumbnail",
        "tags",
    )

    def clean(self, *args, **kwargs):

        if self.duration:
            media_duration = sum(int(x) * 60 ** i for i, x in enumerate(reversed(self.duration.split(':'))))
            self.duration = media_duration

        super().clean(*args, **kwargs)


class Download(models.Model):

    user = models.ForeignKey(CustomUserProfile, on_delete=models.CASCADE)
    media = models.ForeignKey(CustomMedia, on_delete=models.CASCADE)
    download_count = models.SmallIntegerField(blank=False, default=0)
    last = models.DateField(blank=False, default=datetime.now)

