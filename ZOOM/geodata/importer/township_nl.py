import json

from geodata.importer.common import get_json_data
from geodata.models import City, Country, Geolocation


class TownshipNL(object):
    def __init__(self, iso2_code, language):
        self.iso2_code = iso2_code
        self.language = language

    def update(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data('/../data_backup/township_nl.json').get(
            'features')
        for item in items:
            properties = item.get('properties')
            name = properties.get('name').lower()
            city, created = City.objects.get_or_create(
                name=name,
                country=country,
                polygons=json.dumps(item.get('geometry')),
                language=self.language)
            if created:
                Geolocation(content_object=city, tag=name, type='city').save()

            print(item.get('properties').get('name').lower())
