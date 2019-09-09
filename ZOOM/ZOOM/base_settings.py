import os
import sys

from celery.schedules import crontab
from dotenv import find_dotenv, load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(
            os.path.dirname(__file__), '..', 'templates').replace('\\','/'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

sys.path.insert(0, rel('..','lib'))


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

APPEND_SLASH=True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
MEDIA_URL = '/media/'
DATASETS_URL = 'datasets/'

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
)

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ZOOM.urls'

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.gis',
    'rest_framework',
    'api',
    'validate',
    'lib',
    'error_correction',
    'general_tasks',
    'mapping',
    'indicator',
    'geodata',
    'django_extensions',
    'test_without_migrations',
    'metadata',
    'graphene_django',
    'gql',
]

ADMIN_REORDER = (
    'geodata',
    'auth',
)

RQ_SHOW_ADMIN_LINK = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',

    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
    ),
}

LOGIN_REDIRECT_URL = '/admin/'

CORS_ORIGIN_ALLOW_ALL = True
# CORS_URLS_REGEX = r'^/graphql/.*$'
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

ERROR_LOGS_ENABLED = True
DEFAULT_LANG = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

# GraphQL setting

GRAPHENE = {
    'SCHEMA': 'gql.schema.schema',
    'SCHEMA_OUTPUT': 'data/schema.json'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] msg: %(message)s args: %(args)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/logs/mapper.log',
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard'
        },
        'db_log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/logs/db.log',
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['log_file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db_log_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'backoffice': {
            'handlers': ['log_file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# CELERY CONFIG

CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'amqp://localhost'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_BEAT_SCHEDULE = {
    'mapping-iati-data': {
        'task': 'mapping.tasks.mapping_iati_data',
        'schedule': crontab(minute=0, hour=0)
    },
    'cleaning-temp-jsons': {
        'task': 'general_tasks.tasks.clean_temp_geo_jsons',
        'schedule': crontab(minute=0, hour=0)
    },
    'delete-garbage-uploaded-files': {
        'task': 'general_tasks.tasks.delete_garbage_uploaded_files',
        'schedule': crontab(minute=0, hour=0)
    }
}

# TASKS CONFIG

ZOOM_TASK_TIMER = 30
ZOOM_TASK_EMAIL_CONFIRMATION_ENABLE = False
ZOOM_TASK_EMAIL_SENDER = 'devops-zz@zimmermanzimmerman.nl'
ZOOM_TASK_EMAIL_RECEIVER = 'devops-zz@zimmermanzimmerman.nl'
ZOOM_TASK_EMAIL_MAPPING_SUCCESS_SUBJECT = 'ZOOM Mapping Success!'
ZOOM_TASK_EMAIL_MAPPING_FAILED_SUBJECT = 'ZOOM Mapping Failed!'

# this variable very much is dependant on your machine
# and its used to process huge layer data
# IMPORTANT THIS DEPENDS ON THE CORE COUNT ON YOUR MACHINE!
# ALSO NOTE: that using to many workers might be slower,
# than using a little less, because of tasks that need to be
# done before the processes are initiated
POCESS_WORKER_AMOUNT = 2

# LOAD .env FILE

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
