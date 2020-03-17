from ZOOM.settings import *  # NOQA: F403

# Use Docker database service name from docker-compose:
# DATABASES['default']['HOST'] = 'db'  # NOQA: F405

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'zoom',
        'USER': 'zoom',
        'PASSWORD': 'zoom',
        'HOST': 'db',
    },
}

# SEND EMAIL CONFIG

EMAIL_HOST = 'smtp.postmarkapp.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'eb6520ea-eb38-4a11-b1f3-328cdee3ca57'
EMAIL_HOST_PASSWORD = 'eb6520ea-eb38-4a11-b1f3-328cdee3ca57'
EMAIL_USE_TLS = True

# TASKS

ZOOM_TASK_EMAIL_CONFIRMATION_ENABLE = True
ZOOM_TASK_EMAIL_SENDER = 'devops-zz@zimmermanzimmerman.nl'
ZOOM_TASK_EMAIL_RECEIVER = 'devops-zz@zimmermanzimmerman.nl'

# DOCKER RABBIT MQ

CELERY_BROKER_URL = 'amqp://rabbitmq'
CELERY_RESULT_BACKEND = 'amqp://rabbitmq'
