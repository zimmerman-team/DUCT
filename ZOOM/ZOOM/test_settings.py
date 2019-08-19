from ZOOM.production_settings import *

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': ':memory:',
    },
}

REST_FRAMEWORK = {
    'TEST_REQUEST_RENDERER_CLASSES':
    ('rest_framework.renderers.MultiPartRenderer',
     'rest_framework.renderers.JSONRenderer',
     'rest_framework.renderers.TemplateHTMLRenderer')
}
