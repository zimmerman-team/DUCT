FROM python:2.7
LABEL type = zoom-csv(dev)
WORKDIR /src

#Check this
RUN apt-get install -y wget \
  && rm -rf /var/lib/apt/lists

#Check this
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils


RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y python-dev python-pip
RUN apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

# postgresql
#Need to check if all these are nessecary
RUN apt-get install -y sqlite3 # for tests
RUN apt-get install -y libsqlite3-dev # for tests
#RUN apt-get install postgres-10
RUN apt-get install -y postgresql-client
RUN apt-get update
RUN apt-get install -y postgis

RUN apt-get install libpq-dev

# GEOS
RUN apt-get install -y binutils libproj-dev gdal-bin libgeos-dev

RUN apt-get install libsqlite3-mod-spatialite

ADD ZOOM/requirements.txt requirements.txt

ADD . /src/

#CMD

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 777 /src/ZOOM/logs/*.log*

CMD /src/bin/docker-cmd.sh
