import ujson
from geodata.importer.common import get_json_data
from django.contrib.gis.geos import fromstr

from geodata.models import SubNational, Country, Geolocation
import json

class SubnationalImport():
    """
    Wrapper class for all import methods used on the Country model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_polygon(self):
        kenya_counties = self.get_json_data("/../data_backup/kenyan-counties.geojson")

        for k in kenya_counties.get('features'):
            name = k.get('properties').get('COUNTY').lower()
            country = Country.objects.get(name='kenya')
            polygons = json.dumps(k.get('geometry'))

            c, created = SubNational.objects.get_or_create(name=name, country=country, polygons=polygons)
            if created:
                c.save()
                Geolocation(content_object=c, tag=name, type='subnational').save()

