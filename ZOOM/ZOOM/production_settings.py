from ZOOM.base_settings import *

BASE_DIR = os.path.dirname(os.path.realpath(__name__))

DEBUG = False
SECRET_KEY = '__SECRET_KEY_HERE__'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'zoom',
        'USER': 'zoom',
        'PASSWORD': 'zoom',
        'HOST': '127.0.0.1',
        'CONN_MAX_AGE': 500
    },
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
    }
}

API_CACHE_SECONDS = 60 * 60 * 24
ROOT_ORGANISATIONS = []

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_DIRS = (
     os.path.join(BASE_DIR, 'static/'),
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ZOOM.wsgi.application'

ERROR_LOGS_ENABLED = True

try:
    from .local_settings import *
except ImportError:
    pass

