from ZOOM.base_settings import *  # NOQA: F403

DEBUG = True
BASE_DIR = os.path.abspath(  # NOQA: F405
    os.path.join(os.path.dirname(  # NOQA: F405
        os.path.abspath(__file__)  # NOQA: F405
    ), '..')
)
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

MEDIA_ROOT = os.path.join(BASE_DIR, "samples")  # NOQA: F405
STATIC_ROOT = os.path.join(BASE_DIR, 'static_served/')  # NOQA: F405

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'), )  # NOQA: F405

FIXTURE_DIRS = (os.path.join(BASE_DIR, '../fixtures/'), )  # NOQA: F405

API_CACHE_SECONDS = 0

try:
    from .local_settings import *  # NOQA: F401 F403
except ImportError:
    pass
