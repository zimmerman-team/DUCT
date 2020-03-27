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

EMAIL_HOST = 'your_email_host'
EMAIL_PORT = 'your_email_host_port'
EMAIL_HOST_USER = 'your_email_host_user'
EMAIL_HOST_PASSWORD = 'your_email_host_password'
EMAIL_USE_TLS = True

# TASKS

ZOOM_TASK_EMAIL_CONFIRMATION_ENABLE = True
ZOOM_TASK_EMAIL_SENDER = 'your_email_sender'
ZOOM_TASK_EMAIL_RECEIVER = 'your_default_email_receiver'

# DOCKER RABBIT MQ

CELERY_BROKER_URL = 'amqp://rabbitmq'
CELERY_RESULT_BACKEND = 'amqp://rabbitmq'
