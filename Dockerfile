FROM ubuntu:16.04 as build

RUN apt-get -y update

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get -y update --fix-missing

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
    vim \
    git

RUN python3.6 -m pip install pip --upgrade

ENV PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.6/dist-packages"

# Create a directory and copy in all files
RUN mkdir -p /tmp/tippecanoe-src
RUN git clone https://github.com/mapbox/tippecanoe.git /tmp/tippecanoe-src
WORKDIR /tmp/tippecanoe-src

ADD . /src/

RUN ["chmod", "+x", "/src/docker-entrypoint.sh"]

RUN pip install -r /src/ZOOM/requirements.txt

# Build tippecanoe
RUN make \
    && make install

# Remove the temp directory and unneeded packages
WORKDIR /
RUN rm -rf /tmp/tippecanoe-src \
    && apt-get -y remove --purge build-essential && apt-get -y autoremove

RUN chmod 777 /src/ZOOM/logs/*

# run
CMD ["sh","-c","nginx -g 'daemon off;'"]