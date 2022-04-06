from django.conf import settings
from django.core.files.storage import DefaultStorage
from storages.backends.s3boto3 import S3Boto3Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class StaticStorage(S3Boto3Storage):

    try:
        bucket_name = settings.AWS_PUBSTORAGE_BUCKET_NAME
        location = settings.STATICFILES_LOCATION
        gzip = settings.AWS_IS_GZIPPED
        default_acl = 'public-read'
    except:
        pass

if settings.DEBUG:
    s3_static_storage = DefaultStorage()
else:
    s3_static_storage = StaticStorage()


@deconstructible
class PubMediaStorage(S3Boto3Storage):

    try:
        bucket_name = settings.AWS_PUBSTORAGE_BUCKET_NAME
        location = settings.MEDIAFILES_LOCATION
        default_acl = 'public-read'
    except:
        pass

if settings.DEBUG:
    s3_media_storage = DefaultStorage()
else:
    s3_media_storage = PubMediaStorage()


@deconstructible
class PrivMediaStorage(S3Boto3Storage):

    try:
        custom_domain = None
        signature_version = settings.AWS_S3_SIGNATURE_VERSION
        bucket_name = settings.AWS_PRIVSTORAGE_BUCKET_NAME
        location = settings.MEDIAFILES_LOCATION
    except:
        pass

if settings.DEBUG:
    s3_priv_storage = DefaultStorage()
else:
    s3_priv_storage = PrivMediaStorage()
