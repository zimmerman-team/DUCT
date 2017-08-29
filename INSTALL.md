### Prerequisites

Before you can install the ZOOM-CSV-MAPPER, be sure to have the following installed on your machine:

*  Python (2.7)

*  A VPS running Ubuntu (16.04)

### clone the project

```
sudo apt-get install git
git clone https://github.com/zimmerman-zimmerman/ZOOM-CSV-MAPPER.git;  
cd ZOOM-CSV-MAPPER;  
git checkout master;
```

### Install dependencies

Install all the dependencies in the bin/setup/install_dependencies.sh folder.

```
sudo sh bin/setup/install_dependencies.sh
```

Install a python virtual environment

## virtualenv

```
sudo apt-get install python-pip;
sudo pip install virtualenvwrapper;  
export WORKON_HOME=~/envs;
/usr/local/bin/virtualenvwrapper.sh;  
source /usr/local/bin/virtualenvwrapper.sh;  
mkvirtualenv zoom;
workon zoom;
```

Install pip packages

```
pip install --upgrade pip;  
pip install -r ZOOM/requirements.txt;  
```


### Configuration

Create a database

```
sudo -u postgres bash -c "psql -c \"CREATE USER zoom WITH PASSWORD 'zoom';\""
sudo -u postgres bash -c "psql -c \"ALTER ROLE zoom SUPERUSER;\""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE zoom;\""
```

Migrate the database, create a superuser, and run the server (for production, we use nginx/uwsgi).

```
cd ZOOM
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

