FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update --fix-missing

RUN apt-get -y install \
    #Python installs:
    build-essential \
    python3.6 \
    python3.6-dev \
    python3-pip \
    python3.6-venv \
    #Libraries:
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    #For tests:
    sqlite3 \
    libsqlite3-dev \
    #PostgreSQL:
    postgresql-client \
    postgis \
    libpq-dev \
    #GEOS:
    binutils \
    libproj-dev \
    gdal-bin \
    libgeos-dev \
    #Spatialite:
    libsqlite3-mod-spatialite \
    vim

RUN python3.6 -m pip install pip --upgrade

ENV PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.6/dist-packages"

ADD . /src/

RUN pip install -r /src/ZOOM/requirements.txt

RUN chmod 777 /src/ZOOM/logs/*.log*
