import json
from django.contrib.gis.geos import fromstr
from geodata.importer.common import get_json_data
from geodata.models import City, Country


class Cities(object):

    def __init__(self):
        pass

    def update(self):
        items = get_json_data(
            '/../data_backup/cities.json').get('features')
        for item in items:
            geoid = int(item['properties']['GEONAMEID'])
            name = item['properties']['NAME']
            the_country = None
            latitude = item['properties']['LATITUDE']
            longitude = item['properties']['LONGITUDE']
            ascii_name = item['properties']['NAMEASCII']
            alt_name = item['properties']['NAMEALT']
            country_iso2 = item['properties']['ISO_A2']
            namepar = item['properties']['NAMEPAR']
            polygons = json.dumps(item.get('geometry'))

            point_loc_str = 'POINT(' + str(longitude) + ' ' + str(
                latitude) + ')'
            longlat = fromstr(point_loc_str, srid=4326)

            if Country.objects.filter(code=country_iso2).exists():
                the_country = Country.objects.get(code=country_iso2)

            city = City(
                geoname_id=geoid,
                name=name,
                country=the_country,
                location=longlat,
                ascii_name=ascii_name,
                alt_name=alt_name,
                namepar=namepar,
                polygons=polygons
            )

            city.save()

            if item['properties']['FEATURECLA'] == "Admin-0 capital":
                if the_country:
                    the_country.capital_city = city
                    the_country.save()

            print(city.name)
