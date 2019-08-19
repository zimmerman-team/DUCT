from ZOOM.base_settings import *

DEBUG = True
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SECRET_KEY = '__DEV_SECRET_KEY__'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'zoom',
        'USER': 'zoom',
        'PASSWORD': 'zoom',
        'HOST': '127.0.0.1',
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, "samples")
STATIC_ROOT = os.path.join(BASE_DIR, 'static_served/')

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'), )

FIXTURE_DIRS = (os.path.join(BASE_DIR, '../fixtures/'), )

API_CACHE_SECONDS = 0

try:
    from .local_settings import *
except ImportError:
    pass
