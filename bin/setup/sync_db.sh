#!/bin/bash
# todo: peer authentication with zoom user

sudo -u postgres bash -c "psql -c \"CREATE USER zoom WITH PASSWORD 'zoom';\""
sudo -u postgres bash -c "psql -c \"ALTER ROLE zoom SUPERUSER;\""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE zoom;\""

# Run syncdb
sudo -H -u vagrant /home/vagrant/.env/bin/python /vagrant/ZOOM/manage.py migrate --noinput
