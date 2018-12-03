## DUCT: Data Universal Conversion Tool

[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/zimmerman-zimmerman/DUCT/blob/master/LICENSE.MD)


DUCT is Django application which allows user to convert CSV files to a harmonised datastore modelled on the SDMX standard with a standardised output. It provides two different API' to interface the data either to convert (PUT) and extract data in your bespoke IU (GET). DUCT makes use of The Django REST API as a base API and on top of this, it provides GraphQL to connect to your datastore for data modelling, data conversion, data integration and data interfacing.

DUCT has been build as part of Zoom, a Data platform for data informed strategy in combating the aids epidemic in cooperation with Aidsfonds that works towards ending AIDS in a world where all people affected by HIV/AIDS have access to prevention, treatment, care and support and HumanityX who are supporting organisations in the peace, justice and humanitarian sectors to adopt digital innovations in order to increase their impact on society.


## Requirements

| Name                   | Recommended version |
| ---                    | ---       |
| Python                 | 3.6.5     |
| PostgreSQL             | 10.5      |
| Redis                  | 4.0.x     |
| PostGIS                | See: <a href="https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/postgis/">installing PostGIS</a> |
| Ubuntu (Documentation only covers Ubuntu) | (16.04)   |

## Quick start
-------

git clone https://github.com/zimmerman-zimmerman/DUCT.git;  
cd DUCT
sudo sh bin/setup/install_dependencies.sh
pip install -r ZOOM/requirements.txt;
sudo sh bin/setup/sync_db.sh
sudo sh bin/setup/create_django_user.sh
cd ZOOM/scripts
./setup_project.sh
cd ..
python manage.py runserver

or

COMING SOON: If you have docker installed:

cd DUCT
make
docker-compose up

## Documentation
--------

### clone the project

```
sudo apt-get install git
git clone https://github.com/zimmerman-zimmerman/DUCT.git;  
cd DUCT;  
```

### Install dependencies

Install all the dependencies in the bin/setup/install_dependencies.sh folder.

```
sudo sh bin/setup/install_dependencies.sh
```

Install a python virtual environment
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
cd ZOOM
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

Migrate the database, create a superuser, and run the server (for production, we use nginx/gunicorn).

```
cd ZOOM/scripts
sh setup_project.sh
cd ../
python manage.py createsuperuser
python manage.py runserver
```

Eventually, you could add your modifications to the Django configuration in a new file at ZOOM/local_settings.py

### Endpoints Overview

#### Rest endpoints


|URL |Code Loc|
|--- | --- |
|/api/indicators/| api.indicator.views.IndicatorList|
|/api/mapping/|api.mapping.views.MappingJob|
|/api/mapping/get_data|api.mapping.views.get_data|
|/api/mapping/status|api.mapping.views.MappingJobResult|
|/api/metadata/|api.metadata.views.FileListView|
|/api/metadata/<pk>/|api.metadata.views.FileDetailView|
|/api/metadata/sources/|api.metadata.views.FileSourceListView|
|/api/metadata/upload/|api.metadata.views.FileUploadView|
|/api/metadata/sources/<pk>/|api.metadata.views.FileSourceDetailView|
|/api/validate/|api.validate.views.Validate|
|/api/validate/check_file_valid/|api.validate.views.check_file_valid|
|/api/error-correction/|api.error_correction.views.ErrorCorrectionView|


#### GraphQL

|URL |Code Loc|
|--- |--- |
|/graphql|graphene_django.views.GraphQLView|

|Query|Code Loc|
|---| --- |
|allMappings| gql.mapping.schema.Query|
|allIndicators|gql.indicator.schema.Query|
|datapointsAggregation|gql.indicator.schema.Query|
|fileSource|gql.metadata.schema.Query|
|allFileSources|gql.metadata.schema.Query|
|file|gql.metadata.schema.Query|
|allFiles|gql.metadata.schema.Query|
|country|gql.geodata.schema.Query|
|allCountries|gql.geodata.schema.Query|
|geolocation|gql.geodata.schema.Query|
|allGeolocations|gql.geodata.schema.Query|

|Mutation|Code Loc|
|---| --- |
|mapping|gql.mapping.mutation.Mutation|
|indicator|gql.indicator.mutation.Mutation|
|fileSource|gql.metadata.mutation.Mutation|
|file|gql.metadata.mutation.Mutation|

## About the project
--------

* Authors:          <a href="https://www.zimmermanzimmerman.nl/" target="_blank">Zimmerman & Zimmerman</a>
* License:          <a href="https://github.com/zimmerman-zimmerman/DUCT/blob/master/LICENSE.MD" target="_blank">github.com/zimmerman-zimmerman/DUCT/</a>
* Github Repo:      <a href="https://github.com/zimmerman-zimmerman/DUCT/" target="_blank">github.com/zimmerman-zimmerman/DUCT/</a>
* Bug Tracker:     <a href="https://github.com/zimmerman-zimmerman/DUCT/issues" target="_blank">github.com/zimmerman-zimmerman/DUCT/issues</a>


## Can I contribute?
--------

Yes please! We are mainly looking for coders to help on the project. If you are a coder feel free to *Fork* the repository and send us Pull requests!

## Running the tests
-------

###Django Rest API

The rest API endpoints can be tested by:
```
python manage.py test api.<Test Choice>
```
Below is an example of a test that can be run
```
python manage.py test api.mapping.tests.test_file_manual_mapping
```

###GraphQL
