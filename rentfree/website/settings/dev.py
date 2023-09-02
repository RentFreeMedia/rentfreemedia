from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

BASE_URL = '127.0.0.1:8000'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar'
]

# SECURITY WARNING: keep the secret key used in production secret! Edit in .env in project root.
SECRET_KEY = os.environ.get('DOSECRET_KEY')

# Add your site's domain name(s) here.

ALLOWED_HOSTS = [f'{BASE_URL}', '127.0.0.1']
X_FRAME_OPTIONS = 'ALLOW FROM ALL'

# Static files (CSS, JavaScript, Images)

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

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
        'debug_toolbar.middleware.DebugToolbarMiddleware',
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

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

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}


DEBUG_TOOLBAR_CONFIG = {
    # Toolbar options
    'RESULTS_CACHE_SIZE': 3,
    'SHOW_COLLAPSED': True,
    # Panel options
    'SQL_WARNING_THRESHOLD': 100,   # milliseconds
}

WAGTAIL_CACHE = False

WAGTAIL_2FA_REQUIRED = False

STRIPE_TEST_PUBLIC_KEY = os.environ.get('DOSTRIPE_TESTPUB')
STRIPE_TEST_SECRET_KEY = os.environ.get('DOSTRIPE_TESTKEY')
STRIPE_LIVE_MODE = False
DJSTRIPE_WEBHOOK_SECRET = os.environ.get('DOSTRIPE_WHKEY')
DJSTRIPE_USE_NATIVE_JSONFIELD = True
DJSTRIPE_FOREIGN_KEY_TO_FIELD = 'id'
DJSTRIPE_WEBHOOK_URL = r"^subscribe-events/$"

WAGTAILMEDIA = {
    "MEDIA_MODEL": 'website.CustomMedia',
    "MEDIA_FORM_BASE": 'website.mediaform.BaseMediaForm',
    "AUDIO_EXTENSIONS": [],
    "VIDEO_EXTENSIONS": [],
}

try:
    from .local import *
except ImportError:
    pass
