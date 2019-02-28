import json

from geodata.importer.common import get_json_data
from geodata.models import PostCode, Country, Geolocation


class PostCodeNL(object):

    def __init__(self, iso2_code, language):
        self.iso2_code = iso2_code
        self.language = language

    def update(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data(
            '/../data_backup/NL_PC6.json').get('features')
        for item in items:
            properties = item.get('properties')
            code = properties.get('Postcode').lower()
            post_code, created = PostCode.objects.get_or_create(
                code=code,
                country=country,
                polygons=json.dumps(item.get('geometry')),
                language=self.language
            )
            if created:
                Geolocation(
                    content_object=post_code,
                    tag=code,
                    type='postcode'
                ).save()

            print(code)
