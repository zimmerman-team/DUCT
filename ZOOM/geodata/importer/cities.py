import json
from django.contrib.gis.geos import fromstr
from geodata.importer.common import get_json_data
from geodata.models import City, Country, Geolocation


class Cities(object):

    def __init__(self, language):
        self.language = language

    def update(self):
        items = get_json_data(
            '/../data_backup/cities.json').get('features')
        for item in items:
            name = item['properties']['NAME'].lower()
            the_country = None
            latitude = item['properties']['LATITUDE']
            longitude = item['properties']['LONGITUDE']
            ascii_name = item['properties']['NAMEASCII']
            country_iso2 = item['properties']['ISO_A2']
            polygons = json.dumps(item.get('geometry'))
            point_loc_str = 'POINT(' + str(longitude) + ' ' + str(
                latitude) + ')'
            longlat = fromstr(point_loc_str, srid=4326)

            country = None
            if Country.objects.filter(iso2=country_iso2).exists():
                country = Country.objects.get(code=country_iso2)

            try:
                city = City.objects.get(name=name)
            except City.DoesNotExist:
                city = City(
                    name=name,
                    country=country,
                    ascii_name=ascii_name,
                    polygons=polygons,
                    center_longlat=longlat,
                    language=self.language
                )
                city.save()

                try:
                    Geolocation.objects.get(tag=name)
                except Geolocation.DoesNotExist:
                    Geolocation(
                        content_object=city,
                        tag=name,
                        type='city',
                        polygons=polygons,
                        center_longlat=longlat
                    ).save()

            if item['properties']['FEATURECLA'] == "Admin-0 capital":
                if the_country:
                    the_country.capital_city = city
                    the_country.save()

            print(city.name)
