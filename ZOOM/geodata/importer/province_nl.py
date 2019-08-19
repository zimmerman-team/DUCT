import json

from geodata.importer.common import get_json_data
from geodata.models import Country, Geolocation, Province


class ProvinceNL(object):
    def __init__(self, iso2_code, language):
        self.iso2_code = iso2_code
        self.language = language

    def update(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data('/../data_backup/province_nl.json').get(
            'features')
        for item in items:
            properties = item.get('properties')
            name = properties.get('name').lower()
            province, created = Province.objects.get_or_create(
                name=name,
                country=country,
                polygons=json.dumps(item.get('geometry')),
                language=self.language)
            if created:
                Geolocation(content_object=province, tag=name,
                            type='province').save()

            print(item.get('properties').get('name').lower())
