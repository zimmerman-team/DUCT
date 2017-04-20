source ~/.env/bin/activate
# creates super user. Piping method is use to prevent shell prompts
echo "from django.contrib.auth.models import User; User.objects.create_superuser(email='vagrant@zoom.nl', username='vagrant', password='vagrant')" | /vagrant/ZOOM/manage.py shell
deactivate
