from ZOOM.settings import *  # NOQA: F403

# Use Docker database service name from docker-compose:
DATABASES['default']['HOST'] = 'db'  # NOQA: F405
