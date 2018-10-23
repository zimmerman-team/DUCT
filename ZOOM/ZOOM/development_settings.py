# Sample production settings, change as needed
import os
from ZOOM.base_settings import *

DEBUG = True
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

MIDDLEWARE_CLASSES += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS += {
    'debug_toolbar',
}


def custom_show_toolbar(self):
    return True


SECRET_KEY = '__DEV_SECRET_KEY__'

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
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

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, 'static_served/')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, '../fixtures/'),
)

API_CACHE_SECONDS = 0

try:
    from local_settings import *
except ImportError as e:
    print(e)
    pass
