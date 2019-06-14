import json
from django.contrib.gis.geos import fromstr

from geodata.importer.common import get_json_data
from geodata.models import PostCode, Country, Geolocation


class PostCodeNL(object):

    def __init__(self, iso2_code, language):
        self.iso2_code = iso2_code
        self.language = language

    def update_pc4(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data(
            '/../data_backup/PC4.geo.json').get('features')
        for item in items:
            properties = item.get('properties')
            code = properties.get('PC4').lower()
            polygons = json.dumps(item.get('geometry'))
            post_code, created = PostCode.objects.get_or_create(
                code=code,
                country=country,
                polygons=polygons,
                language=self.language
            )
            if created:
                Geolocation(
                    content_object=post_code,
                    tag=code,
                    type='postcode',
                    polygons=polygons
                ).save()

            print(code)

    def update_pc6(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data(
            '/../data_backup/PC6.geo.json').get('features')
        for item in items:
            properties = item.get('properties')
            code = properties.get('PC6').lower()
            polygons = json.dumps(item.get('geometry'))
            post_code, created = PostCode.objects.get_or_create(
                code=code,
                country=country,
                polygons=polygons,
                language=self.language
            )
            if created:
                Geolocation(
                    content_object=post_code,
                    tag=code,
                    type='postcode',
                    polygons=polygons
                ).save()

            print(code)

    def update_pc3(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data(
            '/../data_backup/PC3.geo.json').get('features')
        for item in items:
            properties = item.get('properties')
            code = properties.get('postalcode').lower()
            polygons = json.dumps(item.get('geometry'))
            post_code, created = PostCode.objects.get_or_create(
                code=code,
                country=country,
                polygons=polygons,
                language=self.language
            )
            if created:
                Geolocation(
                    content_object=post_code,
                    tag=code,
                    type='postcode',
                    polygons=polygons
                ).save()

            print(code)

    def update_pc2(self):
        country = Country.objects.get(iso2=self.iso2_code)
        items = get_json_data(
            '/../data_backup/PC2.geo.json').get('features')
        for item in items:
            properties = item.get('properties')
            code = properties.get('postalcode').lower()
            polygons = json.dumps(item.get('geometry'))
            post_code, created = PostCode.objects.get_or_create(
                code=code,
                country=country,
                polygons=polygons,
                language=self.language
            )
            if created:
                Geolocation(
                    content_object=post_code,
                    tag=code,
                    type='postcode',
                    polygons=polygons
                ).save()

            print(code)

    def _updated_pc_centers(self, file):
        centers = get_json_data(file)
        for center in centers:
            try:
                pc = PostCode.objects.get(code=center.lower())
                point_string = ''.join([
                    'POINT(',
                    str(centers[center]["longitude"]),
                    ' ',
                    str(centers[center]["latitude"]),
                    ')'])
                long_lat = fromstr(point_string, srid=4326)
                pc.center_longlat = long_lat
                pc.save()
                try:
                    geolocation = Geolocation.objects.get(tag=pc.code)
                    geolocation.save()
                    print("Updated {code}".format(code=pc.code))
                except Geolocation.DoesNotExist:
                    pass
            except PostCode.DoesNotExist:
                print("Not found {code}:".format(code=center.lower()))

    def update(self):
        self.update_pc2()
        self.update_pc4()
        self.update_pc6()
        self.update_pc3()

    def update_centers(self):
        self._updated_pc_centers('/../data_backup/PC2_centers.json')
        self._updated_pc_centers('/../data_backup/PC3_centers.json')
        self._updated_pc_centers('/../data_backup/PC4_centers.json')
        self._updated_pc_centers('/../data_backup/PC6_centers.json')
