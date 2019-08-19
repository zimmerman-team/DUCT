import json

from django.contrib.gis.geos import fromstr

from geodata.importer.common import get_json_data
from geodata.models import Country, Geolocation, Region

from shapely.geometry import shape, mapping
from shapely.ops import cascaded_union


class CountryImport(object):
    """
    Wrapper class for all import methods used on the Country model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_alt_name(self):
        # We don't use an alternative name anymore
        admin_countries = self.get_json_data(
            "/../data_backup/alternative_names.json")
        for k in admin_countries:
            country_iso2 = k.get('iso2').lower()
            name = k.get('name').lower()
            c, created = Country.objects.get_or_create(name=name,
                                                       iso2=country_iso2)

            if created:
                c.save()
                Geolocation(content_object=c, tag=name, type='country').save()
            else:
                try:
                    Geolocation.objects.get(tag=name)
                except Geolocation.DoesNotExist:
                    Geolocation(content_object=c, tag=name,
                                type='country').save()

    def update_polygon(self):
        admin_countries = self.get_json_data(
            "/../data_backup/allcountrycodes.json")

        for k in admin_countries:  # .get('features'):
            country_iso2 = k.get('alpha-2').lower()
            name = k.get('name').lower()
            country_iso3 = k.get('alpha-3').lower()

            if not country_iso2:
                continue

            c, created = Country.objects.get_or_create(iso2=country_iso2,
                                                       iso3=country_iso3,
                                                       name=name,
                                                       primary_name=True)
            if created:
                c.save()

            # Add or update geolocation
            try:
                geolocation = Geolocation.objects.get(tag=c.name)
            except Geolocation.DoesNotExist:
                geolocation = Geolocation(content_object=c,
                                          tag=c.name,
                                          type='country')

            geolocation.save()
            print('Country : {name}:'.format(name=c.name))

        poly_countries = self.get_json_data(
            "/../data_backup/country_data.json").get('features')
        for k in poly_countries:  # .get('features'):
            if 'iso2' in k.get('properties'):
                iso2 = k.get('properties').get('iso2').lower()
                filtered_set = Country.objects.filter(iso2=iso2,
                                                      primary_name=True)
                if len(filtered_set) > 0:
                    c = filtered_set[0]
                else:
                    name = k.get('properties').get('name').lower()
                    c = Country(name=name, iso2=iso2, primary_name=True)
                    c.save()

                c.polygons = json.dumps(k.get('geometry'))
                c.save()

                # Add or update geolocation
                try:
                    geolocation = Geolocation.objects.get(tag=c.name)
                except Geolocation.DoesNotExist:
                    geolocation = Geolocation(content_object=c,
                                              tag=c.name,
                                              type='country')

                geolocation.save()
                print('Polygon : {name}:'.format(name=c.name))

    def update_country_center(self):
        country_centers = self.get_json_data(
            "/../data_backup/country_center.json")

        for c in country_centers:
            if Country.objects.filter(iso2=c.lower()).exists():

                current_country = Country.objects.get(iso2=c.lower(),
                                                      primary_name=True)

                point_loc_str = ''.join([
                    'POINT(',
                    str(country_centers[c]["longitude"]), ' ',
                    str(country_centers[c]["latitude"]), ')'
                ])
                longlat = fromstr(point_loc_str, srid=4326)
                current_country.center_longlat = longlat
                current_country.save()
                Geolocation(tag=current_country.name,
                            content_object=current_country,
                            type='country').save()

    def update_regions(self):
        country_regions = self.get_json_data(
            "/../data_backup/country_regions.json")
        for cr in country_regions:
            the_country = None

            country_iso2 = cr['iso2'].lower()
            region_dac_code = cr['dac_region_code'].lower()
            region_dac_name = cr['dac_region_name'].lower()

            # Get country by iso2
            if Country.objects.filter(iso2=country_iso2).exists():
                the_country = Country.objects.get(iso2=country_iso2,
                                                  primary_name=True)

            # Update or create region
            if Region.objects.filter(code=region_dac_code).exists():
                the_region = Region.objects.get(code=region_dac_code)
                the_region.name = region_dac_name
                the_region.save()
            else:
                the_region = Region(code=region_dac_code, name=region_dac_name)
                the_region.save()

            # Create geolocation record by region
            if not Geolocation.objects.filter(tag=region_dac_name).exists():
                Geolocation(tag=region_dac_name,
                            content_object=the_region,
                            type='region').save()

            # Update the region of the country
            if the_country:
                if the_country.region is None:
                    the_country.region = the_region
                    the_country.save()

    def update_hd_polygons(self):
        """
        Update HD Polygons provided by Jim
        """
        poly_countries = self.get_json_data(
            "/../data_backup/countries_080419.json").get('features')
        for k in poly_countries:  # .get('features'):
            if 'iso_a2' in k.get('properties'):
                iso2 = k.get('properties').get('iso_a2').lower()

                print('Updated HD polygon -> {iso2}'.format(iso2=iso2))

                try:
                    country = Country.objects.get(iso2=iso2)
                    country.polygons = json.dumps(k.get('geometry'))
                    country.save()

                    print('Updated HD polygon -> country {iso2}'.format(
                        iso2=iso2))

                    geolocation = Geolocation.objects.get(iso2=iso2)
                    geolocation.save()

                    print('Updated HD polygon -> geolocation {iso2}'.format(
                        iso2=iso2))
                except Country.DoesNotExist:
                    pass

    # this basically merges the country polygons associated with a region
    # thus forming the region polygon and from that making the center coordinates
    def update_region_polygons_centers(self):
        for region in Region.objects.all():
            print('region', region.name)
            count_polygons = []

            for country in region.country_set.all():
                if country.polygons:
                    shapely_pol = shape(json.loads(country.polygons.json))
                    count_polygons.append(shapely_pol.buffer(0))

            # and we also save the region code to the geolocations
            # iso3, cause in the previous script, the initial load script
            # it wasn't saved
            geolocation = Geolocation.objects.filter(tag=region.name).get()
            geolocation.iso3 = region.code

            region_layer = cascaded_union(count_polygons)
            region_layer_json = mapping(region_layer)

            if 'geometries' in region_layer_json and len(
                    region_layer_json['geometries']) == 0:
                print('exception: ', 'No Country geometries found')
                print('region: ', region.name)
            else:
                region_center_json = mapping(region_layer.centroid)

                layer_json_string = json.dumps(region_layer_json)
                center_json_string = json.dumps(region_center_json)

                region.center_longlat = center_json_string
                region.polygons = layer_json_string
                region.save()
                # we also save the polygons and center long lats
                # to the appropriate geolocation object
                geolocation.polygons = layer_json_string
                geolocation.center_longlat = center_json_string

            geolocation.save()
