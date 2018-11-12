from django.contrib.gis.geos import fromstr
from geodata.models import Region, Geolocation
from geodata.importer.common import get_json_data
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis import geos
import pandas as pd
import os
import json

class RegionImport():
    """
    Wrapper class for all import methods used on the Region model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_region_center(self):
        region_poly = self.get_json_data("/../data_backup/continents.json")

        for region in  region_poly.get('features'):
            name = region.get('properties').get('CONTINENT').lower()
            polygon = json.dumps(region.get('geometry'))
            instance, created = Region.objects.get_or_create(name=name, polygons=polygon)
            if created:
                instance.save()
                Geolocation(content_object=instance, tag=name, type='region').save()

        region_centers = self.get_json_data("/../data_backup/region_center_locations.json")

        '''for r in region_centers:
            if Region.objects.filter(code=r).exists():
                current_region = Region.objects.get(code=r)
                point_loc_str = 'POINT(%s %s)' % (str(region_centers[r]["longitude"]), str(region_centers[r]["latitude"]))
                longlat = fromstr(point_loc_str, srid=4326)
                current_region.center_longlat = longlat
                current_region.save()'''


