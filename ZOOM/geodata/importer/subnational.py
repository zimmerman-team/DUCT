from geodata.importer.common import get_json_data

from geodata.models import SubNational, Country, Geolocation
import json


class SubnationalImport(object):
    """
    Wrapper class for all import methods used on the Country model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_polygon(self):
        kenya_counties = self.get_json_data("/../data_backup/counties.json")

        for k in kenya_counties.get('features'):
            name = k.get('properties').get('COUNTY_NAM')
            if name:
                name = name.lower()
                country = Country.objects.get(name='kenya')
                polygons = json.dumps(k.get('geometry'))
                print(name)

                c, created = SubNational.objects.get_or_create(
                    name=name, country=country, polygons=polygons
                )
                if created:
                    c.save()
                    Geolocation(
                        content_object=c,
                        tag=name,
                        type='subnational'
                    ).save()
