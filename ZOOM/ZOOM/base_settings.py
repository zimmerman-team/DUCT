# Django settings for OIPA project.
import sys
import os
# from django.core.urlresolvers import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# LOGIN_URL = reverse_lazy('two_factor:login')
# LOGOUT_URL = '/logout'
# DATA_UPLOAD_MAX_NUMBER_FIELDS = 3000

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

INSTALLED_APPS = [
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
    'manual_mapping',
    'geodata.apps.GeodataConfig',
    'task_queue',
    'djsupervisor',
    'django_extensions',
    'test_without_migrations',
    'admin_reorder',
]

ADMIN_REORDER = (
    'geodata',
    'auth',
)

RQ_SHOW_ADMIN_LINK = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# REST_FRAMEWORK = {
#     'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPagination',
#     'PAGE_SIZE': 10,
#     'DEFAULT_FILTER_BACKENDS': (
#         'rest_framework.filters.DjangoFilterBackend',
#     ),
#     'DEFAULT_PARSER_CLASSES': (
#         'rest_framework.parsers.JSONParser',
#     ),
#     'DEFAULT_RENDERER_CLASSES': (
#         'rest_framework.renderers.BrowsableAPIRenderer',
#         'rest_framework.renderers.JSONRenderer',
#         'api.renderers.PaginatedCSVRenderer',
#         # 'rest_framework_csv.renderers.CSVRenderer',
#     ),
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

GRAPPELLI_ADMIN_TITLE = 'ZOOM admin'
# ADMINFILES_UPLOAD_TO = 'csv_files'
LOGIN_REDIRECT_URL = '/admin/'

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_URLS_REGEX = r'^/api/.*$'
# CORS_ALLOW_METHODS = ('GET',)

# IATI_PARSER_DISABLED = False
# CONVERT_CURRENCIES = True
# ROOT_ORGANISATIONS = []

ERROR_LOGS_ENABLED = True

DEFAULT_LANG = None
