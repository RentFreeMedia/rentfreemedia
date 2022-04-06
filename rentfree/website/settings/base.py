"""
Django base settings for website project.
"""
import os
from pathlib import Path

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth_2fa',
    'allauth.account',
    'allauth.socialaccount',
    'users',
    'djstripe',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "django.contrib.sitemaps",
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'django_summernote',
    'search',

    'modelcluster',
    'taggit',
    'betterforms',
    'dbtemplates',
    'drip',
    'post_office',
    'storages',
    'stripe',
    'payments',
    'videos_id',
    'wagtailcache',
    'wagtail_personalisation',
    'wagtailmedia',
    'wagtailmarkdown',
    'wagtail_2fa',

    'django_bootstrap5',
    'comment',
    'wagtail.sites',
    'wagtail.embeds',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.forms',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.redirects',
    'wagtail.contrib.settings',
    'wagtail.contrib.styleguide',
    'wagtail.contrib.table_block',
    'website'
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'

ROOT_URLCONF = 'website.urls'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True

USE_I18N = True

USE_L10N = True

AUTH_USER_MODEL = 'users.CustomUser'

INTERNAL_IPS = [
    '127.0.0.1',
    '107.202.13.161',
    '192.168.1.76',
    '192.168.1.82',
]

WAGTAIL_SITE_NAME = os.environ.get('DOSITE_NAME')
WAGTAIL_USER_TIME_ZONES = os.environ.get('DOTIME_ZONES').split(',')

SITE_ID = 1

ACCOUNT_ADAPTER = 'allauth_2fa.adapter.OTPAdapter'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/profile/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/subscribe/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = WAGTAIL_SITE_NAME + ' - '
ACCOUNT_FORMS = {
    'login': 'users.forms.CustomLoginForm',
    'signup': 'users.forms.CustomSignupForm',
    'add_email': 'users.forms.CustomAddEmailForm',
    'change_password': 'users.forms.CustomChangePasswordForm',
    'set_password': 'users.forms.CustomSetPasswordForm',
    'reset_password': 'users.forms.CustomResetPasswordForm',
    'reset_password_from_key': 'users.forms.CustomResetPasswordKeyForm',
    'disconnect': 'users.forms.CustomSocialDisconnectForm',
}
SOCIALACCOUNT_FORMS = {
    'signup': 'users.forms.CustomSocialSignupForm',
    'disconnect': 'users.forms.CustomSocialDisconnectForm'
}
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

DRIP_MESSAGE_CLASSES = {
    'default': 'drip.drips.DripMessage'
}

PHONENUMBER_DB_FORMAT = 'E164'
PHONENUMBER_DEFAULT_REGION = 'US'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TAGGIT_CASE_INSENSITIVE = True

WAGTAIL_COMMENTS_RELATION_NAME = 'wagtail_admin_comments'

WAGTAILADMIN_COMMENTS_ENABLED = True

WAGTAILMARKDOWN = {
    # ...
    'extensions': ['toc', 'sane_lists', 'extra', 'codehilite', 'nl2br', 'wikilinks']
}

WAGTAILMARKDOWN = {
    # ...
    'allowed_tags': [
        'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i', 'tt', 
        'pre', 'em', 'strong', 'ul', 'dl', 'dd', 'dt', 'code', 'img', 'a', 'table', 
        'tr', 'th', 'td', 'tbody', 'caption', 'colgroup', 'thead', 'tfoot', 'blockquote', 
        'hr', 'br', 'small', 'sub', 'sup',
    ],
    'allowed_styles': [
        'color', 'background-color', 'font-family', 'font-weight', 'font-size', 'width', 
        'height', 'text-align', 'border', 'border-top', 'border-bottom', 'border-left', 
        'border-right', 'padding', 'padding-top', 'padding-bottom', 'padding-left', 'padding-right', 
        'margin', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right',
    ],
    'allowed_attributes': {'*': ['class', 'style', 'id'],
            'a': ['href', 'target', 'rel'],
            'img': ['src', 'alt'],
            'tr': ['rowspan', 'colspan'],
            'td': ['rowspan', 'colspan', 'align'],
    }

}

WAGTAIL_USER_EDIT_FORM = 'website.forms.CustomUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'website.forms.CustomUserCreationForm'
WAGTAIL_USER_CUSTOM_FIELDS = [
    'user_name',
    'url',
    'is_mailsubscribed',
    'is_paysubscribed',
    'is_smssubscribed',
    'is_newuserprofile',
    'stripe_customer',
    'stripe_subscription',
    'stripe_paymentmethod',
    'download_resets'
]

WAGTAILSVG_UPLOAD_FOLDER = 'svg'

STATICFILES_DIRS = [
    f'{BASE_DIR}/website/templates/static/'
]

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        # example: override normal Boto credentials specifically for Anymail
        "aws_access_key_id": os.getenv('DOEMAIL_USER'),
        "aws_secret_access_key": os.getenv('DOEMAIL_PASS'),
        "region_name": "us-east-1",
        # override other default options
        "config": {
            "connect_timeout": 30,
            "read_timeout": 30,
        }
    },
}

SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'disable_attachment': True,
    'summernote': {
        'width': '100%',
        'height': '480px'
    }
}

BASIC_AUTH_REALM = 'Administration'


PROFILE_APP_NAME = 'users'
PROFILE_MODEL_NAME = 'CustomUser'
COMMENT_PROFILE_API_FIELDS = ('user_name')
COMMENT_USER_API_FIELDS = ['id', 'user_name']
COMMENT_PER_PAGE = 50
COMMENT_FLAGS_ALLOWED = 1
COMMENT_SHOW_FLAGGED = True
COMMENT_FROM_EMAIL = os.environ.get('DOEMAIL_ADDR')
COMMENT_ALLOW_BLOCKING_USERS = True
COMMENT_ALLOW_MODERATOR_TO_BLOCK = True

MAX_UPLOAD_SIZE = 4294967296
