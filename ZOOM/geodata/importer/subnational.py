import json
from django.contrib.gis.geos import fromstr

from geodata.importer.common import get_json_data
from geodata.models import SubNational, Country, Geolocation


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

    def update_kenya(self):
        kenya_counties = self.get_json_data("/../data_backup/counties.json")

        for k in kenya_counties.get('features'):
            name = k.get('properties').get('COUNTY_NAM')
            if name:
                name = name.lower()
                polygons = json.dumps(k.get('geometry'))
                print(name)

                sub_nationals = SubNational.objects.filter(name=name)
                if sub_nationals:
                    sn = sub_nationals.first()
                    sn.polygons = polygons
                    sn.save()

                    print('Updated Sub national : {name}'.format(name=name))

                    try:
                        geolocation = Geolocation.objects.get(tag=name)
                        geolocation.save()

                        print('Updated geolocation: {name}'.format(name=name))
                    except Geolocation.DoesNotExist:
                        pass

    def update_kenya_county_centers(self):
        county_centers = self.get_json_data(
            "/../data_backup/kenya_county_centers.json")

        for c in county_centers:
            if SubNational.objects.filter(name=c.lower()).exists():
                sub_national = SubNational.objects.get(name=c.lower())

                point_loc_str = ''.join([
                    'POINT(',
                    str(county_centers[c]["longitude"]),
                    ' ',
                    str(county_centers[c]["latitude"]),
                    ')'])
                longlat = fromstr(point_loc_str, srid=4326)

                sub_national.center_longlat = longlat
                sub_national.save()

                try:
                    geolocation = Geolocation.objects.get(
                        tag=sub_national.name.lower()
                    )
                    geolocation.save()

                    print('Update long lat geolocation: {name}'.format(
                        name=sub_national.name)
                    )
                except Geolocation.DoesNotExist:
                    print('Not found geolocation not fount: {name}'.format(
                        name=c.lower())
                    )
