import json

from django.test import TestCase
from graphene.test import Client

from geodata.models import Country, Geolocation, Region
from gql.schema import schema
from gql.tests import factory


class GeolocationsTestCase(TestCase):

    def setUp(self):
        alb = factory.CountryFactory(name='Albania', iso2='al', iso3='alb')
        factory.GeolocationFactory(
            tag='albania',
            iso2='al',
            iso3='alb',
            object_id=alb.id,
            content_type_id=16,
            type='country')
        asia = factory.RegionFactory(
            name='asia'
        )
        factory.GeolocationFactory(
            tag='asia',
            iso2='',
            iso3='',
            object_id=asia.id,
            content_type_id=17,
            type='region')
        self.client = Client(schema)

    def test_allGeolocation(self):
        geolocation = Geolocation.objects.first()
        query = """
            {allGeolocations
                {edges
                    {node 
                        {
                            id
                            entryId
                            tag
                        }
                    } 
                }
            }    
            """

        result = self.client.execute(query)
        self.assertEqual(result['data']['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation.tag)

    def test_allGeolocation_region_polygons(self):
        # Get region record
        region = Region.objects.first()
        polygons = region.polygons
        polygons_in_json = polygons.geojson

        # GraphQL Query
        query = """
            {allGeolocations(tag:"asia") {
                edges {
                    node {
                        id
                        tag
                        region {
                            name
                            polygons
                            }
                        }
                    }
                }
            }
            """
        result = schema.execute(query)
        # Check if polygons at the current record has
        # the same coordinates with the GraphQL query
        result_polygons = json.loads(
            result.data['allGeolocations']['edges'][0]['node']['region'][
                'polygons']
        )
        result_polygons_in_dict = json.loads(result_polygons)
        # The centerLonglat is JSONString, so it is needed to convert again
        # to the Python dictionary
        polygons_in_dict = json.loads(polygons_in_json)
        self.assertEqual(polygons_in_dict['coordinates'],
                         result_polygons_in_dict[
                             'coordinates'])

    def test_region_centerlonglat(self):

        # Get country record
        region = Region.objects.first()
        center_longlat = region.center_longlat
        center_longlat_in_json = center_longlat.geojson
        # GraphQL Query
        query = """
                    {allGeolocations(tag:"asia")
                        {edges
                            {node 
                                {
                                    
                                    entryId
                                    tag
                                    region{
                                        centerLonglat}
                                }
                            } 
                        }
                    }    
                """
        result = schema.execute(query)
        # Check if center_longlat at the current record has
        # the same coordinates with the GraphQL query
        result_center_longlat = json.loads(
            result.data['allGeolocations']['edges'][0]['node']['region'][
                'centerLonglat']
        )
        # The centerLonglat is JSONString, so it is needed to convert again
        # to the Python dictionary
        result_center_longlat_in_dict = json.loads(result_center_longlat)
        center_longlat_in_dict = json.loads(center_longlat_in_json)
        self.assertEqual(center_longlat_in_dict['coordinates'],
                         result_center_longlat_in_dict['coordinates'])
