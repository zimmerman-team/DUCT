from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
from geodata.models import Geolocation, Country,Region
from graphene.test import Client
import json


class GeolocationsTestCase(TestCase):

    def setUp(self):
        self.dummy_geolocation = factory.GeolocationFactory.create()
        self.dummy_region = factory.RegionFactory.create()
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


