# Django settings for ZOOM project.
import sys
import os


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            #'loaders': [
            #    ('django.template.loaders.cached.Loader', [
            #        'django.template.loaders.filesystem.Loader',
            #        'django.template.loaders.app_directories.Loader',
            #    ]),
            #],
        },
    },
]

def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

sys.path.insert(0, rel('..','lib'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9(vv@q+jp25=ud9k&5*=+c_4gr=2e^ubx-)h^42*kw6qn*wk8w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'Europe/Amsterdam'

LANGUAGE_CODE = 'en-us'

APPEND_SLASH=True

SITE_ID = 1

#TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
MEDIA_URL = '/media/'

# Additional locations of static files
# STATICFILES_DIRS = (
#      os.path.join(BASE_DIR, 'static/'),
# )

# URL for static files
STATIC_URL = "/static/"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


MIDDLEWARE_CLASSES = [
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django_otp.middleware.OTPMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'ZOOM.urls'

# Application definition

INSTALLED_APPS = (
    'django_rq',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grappelli',
    'django.contrib.admin',
    'autocomplete_light',
    'django.contrib.gis',
    'validate',
    'lib',
    'indicator'
    'manual_mapping',
    'geodata.apps.GeodataConfig',
    'task_queue',
    'admin_reorder',
)

ADMIN_REORDER = (
    'geodata',
    'auth',
)

RQ_SHOW_ADMIN_LINK = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# MIDDLEWARE_CLASSES = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
# )



# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]




# WSGI_APPLICATION = 'ZOOM.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 3600,
    },
    'parser': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 5400,
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'zoom',
        'USER': 'zoom',
        'PASSWORD': 'zoom',
        'HOST': '127.0.0.1',
    },
}


FIXTURE_DIRS = (
     os.path.join(BASE_DIR, '../fixtures/'),
)


GRAPPELLI_ADMIN_TITLE = 'OIPA admin'
# ADMINFILES_UPLOAD_TO = 'csv_files'
LOGIN_REDIRECT_URL = '/admin/'

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_URLS_REGEX = r'^/api/.*$'
# CORS_ALLOW_METHODS = ('GET',)

# IATI_PARSER_DISABLED = False
# CONVERT_CURRENCIES = True
# ROOT_ORGANISATIONS = []

# ERROR_LOGS_ENABLED = True

DEFAULT_LANG = None

