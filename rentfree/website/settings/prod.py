from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

BASE_URL = os.environ.get('DOBASE_URL')
CDN_URL = os.environ.get('DOCDN_URL')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

#Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# SECURITY WARNING: keep the secret key used in production secret! Edit in .env in project root.
SECRET_KEY = os.environ.get('DOSECRET_KEY')

# Add your site's domain name(s) here.

ALLOWED_HOSTS = [f'{BASE_URL}', 'www.' + f'{BASE_URL}', '127.0.0.1']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
USE_X_FORWARDED_PORT = True

# Static files (CSS, JavaScript, Images)

STATIC_ROOT = os.environ.get('DOCDN_URL')
STATIC_URL = f'https://{STATIC_ROOT}/static/'
MEDIA_URL = f'https://{STATIC_ROOT}/media/'
AWS_ACCESS_KEY_ID = os.environ.get('DOACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('DOSECRET_ACCESS_KEY')
AWS_DEFAULT_ACL = os.environ.get('DODEFAULT_ACL')

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'custom_storages.PubMediaStorage'
PRIV_MEDIA_LOCATION = 'premium_media'
PRIV_MEDIA_STORAGE = 'custom_storages.PrivMediaStorage'
AWS_PUBSTORAGE_BUCKET_NAME = os.environ.get('DOPUB_BUCKET')
AWS_PRIVSTORAGE_BUCKET_NAME = os.environ.get('DOPRIV_BUCKET')
AWS_S3_REGION_NAME = os.environ.get('DOAWS_REGION')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('DOCDN_URL')
AWS_IS_GZIPPED = os.environ.get('DOBUCKET_ZIP')
AWS_S3_SIGNATURE_VERSION = os.environ.get('DOAWS_SIGVER')

AWS_HEADERS = {
    'CacheControl': 'max-age=3600'
}
# only required with Digital Ocean spaces, not on S3-Cloudfront
AWS_S3_REGION_NAME = os.environ.get('DOAWS_REGION')
AWS_S3_URL = os.environ.get('DOPROVIDER_URL')
AWS_S3_ENDPOINT_URL = 'https://' + f'{AWS_S3_REGION_NAME}' + '.' + f'{AWS_S3_URL}'
# most only required in development, anymail sends API mail by... API, see POST_OFFICE section
EMAIL_BACKEND = 'post_office.EmailBackend'
EMAIL_HOST = os.environ.get('DOEMAIL_HOST')
EMAIL_PORT = os.environ.get('DOEMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('DOEMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DOEMAIL_PASS')
EMAIL_USE_TLS = os.environ.get('DOEMAIL_TLS')

# Default email address used to send messages from the website.
DEFAULT_FROM_EMAIL = os.environ.get('DOEMAIL_ADMIN') + ' <' + os.environ.get('DOEMAIL_ADDR') + '>'

# A list of people who get error notifications.
EMAIL_ADMIN = os.environ.get('DOEMAIL_ADMIN')
EMAIL_ADDR = os.environ.get('DOEMAIL_ADDR')

# A list in the same format as ADMINS that specifies who should get broken link
# (404) notifications when BrokenLinkEmailsMiddleware is enabled.
MANAGERS = f'{EMAIL_ADMIN}'

# Email address used to send error messages to ADMINS.
SERVER_EMAIL = f'{EMAIL_ADDR}'

MIDDLEWARE = [
        'wagtailcache.cache.UpdateCacheMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_otp.middleware.OTPMiddleware',
        'allauth_2fa.middleware.AllauthTwoFactorMiddleware',
        'wagtail_2fa.middleware.VerifyUserPermissionsMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'wagtail.contrib.redirects.middleware.RedirectMiddleware',
        'wagtailcache.cache.FetchFromCacheMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DODB_NAME'),
        'USER': os.environ.get('DODB_USER'),
    'PASSWORD': os.environ.get('DODB_PASS'),
    'HOST': os.environ.get('DODB_HOST'),
    'PORT': os.environ.get('DODB_PORT'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',
        'KEY_PREFIX': 'wagtailcache',
        'TIMEOUT': 3600, # one hour (in seconds)
    }
}

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'payments' / 'templates',
            BASE_DIR / 'search' / 'templates',
            BASE_DIR / 'users' / 'templates',
            BASE_DIR / 'website' / 'templates',
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
            'loaders': [
                #'dbtemplates.loader.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
    {
        'BACKEND': 'post_office.template.backends.post_office.PostOfficeTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
            ]
        }
    }
]

POST_OFFICE = {
    'TEMPLATE_ENGINE': 'post_office',
    'LOG_LEVEL': 1, # Database log: 0 = none, 1 = failed, 2 = all
    'BATCH_SIZE': 50,
    'BACKENDS': {
        'default': 'django.core.mail.backends.smtp.EmailBackend',
    }
}

WAGTAIL_CACHE = True

WAGTAIL_2FA_REQUIRED = True
WAGTAIL_2FA_OTP_TOTP_NAME = os.environ.get('DOBASE_URL')

STRIPE_TEST_PUBLIC_KEY = os.environ.get('DOSTRIPE_TESTPUB')
STRIPE_TEST_SECRET_KEY = os.environ.get('DOSTRIPE_TESTKEY')
STRIPE_LIVE_PUBLIC_KEY = os.environ.get('DOSTRIPE_LIVEPUB')
STRIPE_LIVE_SECRET_KEY = os.environ.get('DOSTRIPE_LIVEKEY')
STRIPE_LIVE_MODE = os.environ.get('DOSTRIPE_LIVE')
DJSTRIPE_WEBHOOK_SECRET = os.environ.get('DOSTRIPE_WHKEY')
DJSTRIPE_USE_NATIVE_JSONFIELD = True
DJSTRIPE_FOREIGN_KEY_TO_FIELD = 'id'
DJSTRIPE_WEBHOOK_URL = DJSTRIPE_WEBHOOK_URL = r'^subscribe-events/$'

WAGTAILMEDIA = {
    "MEDIA_MODEL": 'website.CustomMedia',
    "MEDIA_FORM_BASE": 'website.mediaform.BaseMediaForm',
    "AUDIO_EXTENSIONS": [],
    "VIDEO_EXTENSIONS": [],
}

if os.environ.get('DOBSTRAP_URL'):
    BOOTSTRAP5 = {
        "css_url": os.environ.get('DOBSTRAP_URL'),
        "javascript_url": {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
            "integrity": "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
            "crossorigin": "anonymous",
        }
    }
else:
    BOOTSTRAP5 = {
        "css_url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
        "javascript_url": {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
            "integrity": "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
            "crossorigin": "anonymous",
        }
    }

try:
    from .local import *
except ImportError:
    pass

