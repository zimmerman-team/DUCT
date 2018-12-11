### Activate virtual environment before running this ###
# creates super user. Piping method is use to prevent shell prompts
echo "from django.contrib.auth.models import User; User.objects.create_superuser(email='zoom@zoom.nl', username='zoom', password='zoom')" | ../../ZOOM/manage.py shell
deactivate
