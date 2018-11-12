from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
from geodata.models import Geolocation, Country
from graphene.test import Client


class GeolocationsTestCase(TestCase):

    def setUp(self):
        self.dummy_geolocation = factory.GeolocationFactory.create()
        self.client = Client(schema)

    def test_allCountries(self):
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

