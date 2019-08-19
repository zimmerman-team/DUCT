import datetime
import time

import django_rq
from django.conf import settings
from django_rq import job
from redis import Redis
from rq import Connection, Queue, Worker
from rq.job import Job

from manual_mapping.manual_mapper import manual_mapper

redis_conn = Redis()

###############################
######## GEODATA TASKS ########
###############################


@job
def update_all_geo_data():
    queue = django_rq.get_queue("default")
    queue.enqueue(update_region_data)
    queue.enqueue(update_country_data)
    queue.enqueue(update_adm1_region_data)
    queue.enqueue(update_city_data)


@job
def get_new_geoapp_data_from_iati_api():
    from django.core import management
    management.call_command('get_geoapp_data_from_iati_registry',
                            verbosity=0,
                            interactive=False)


@job
def update_region_data():
    from geodata.importer.region import RegionImport
    ri = RegionImport()
    ri.update_region_center()


@job
def update_country_data():
    from geodata.importer.country import CountryImport
    ci = CountryImport()
    ci.update_country_center()
    ci.update_polygon()
    ci.update_regions()
    ci.update_alt_name()


@job
def update_adm1_region_data():
    from geodata.importer.admin1region import Adm1RegionImport
    ai = Adm1RegionImport()
    ai.update_from_json()


@job
def update_city_data():
    from geodata.importer.city import CityImport
    ci = CityImport()
    ci.update_cities()


###############################
#### MANUAL MAPPING TASKS #####
###############################


@job
def manual_mapping_job(data):
    context = manual_mapper(data)
    return context
