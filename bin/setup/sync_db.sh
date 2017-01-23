#!/bin/bash
# todo: peer authentication with zoom user
sudo -u postgres bash -c "psql -c \"DROP DATABASE [IF EXISTS] 'zoom';\""
sudo -u postgres bash -c "psql -c \"CREATE USER zoom WITH PASSWORD 'zoom';\""
sudo -u postgres bash -c "psql -c \"ALTER ROLE zoom SUPERUSER;\""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE zoom;\""

# Run syncdb
print
sudo -H -u osboxes /home/osboxes/.env/bin/python /ZOOM/manage.py migrate --noinput
