import json
from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
from geodata.models import Country


class CountryTestCase(TestCase):

    def setUp(self):
        factory.CountryFactory.create()

    def test_allCountries(self):
        country = Country.objects.first()
        query = """
            {allCountries
                {edges
                    {node 
                        {
                            id
                            entryId
                            name
                        }
                    } 
                }
            }    
            """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['name'], country.name)

    def test_countryCenterLongLat(self):
        # TODO: please make the test for the field polygons
        # The test code is the same logic with the bellow code.
        # ----------------------
        # Get country record
        country = Country.objects.first()
        coordinates = [coord for coord in country.center_longlat]
        # GraphQL Query
        query = """
                    {allCountries
                        {edges
                            {node 
                                {
                                    id
                                    entryId
                                    name
                                    centerLonglat
                                }
                            } 
                        }
                    }    
                """
        result = schema.execute(query)
        # Check if center_longlat at the current record has
        # the same coordinates with the GraphQL query
        center_longlat = json.loads(
            result.data['allCountries']['edges'][0]['node']['centerLonglat']
        )
        # The centerLonglat is JSONString, so it is needed to convert again
        # to the Python dictionary
        center_longlat = json.loads(center_longlat)
        self.assertEqual(coordinates, center_longlat['coordinates'])

    def test_countryPolygons(self):

        # Get country record
        country = Country.objects.first()
        polygons = country.polygons
        polygons_in_json = polygons.geojson

        # GraphQL Query
        query = """
                    {allCountries
                        {edges
                            {node 
                                {
                                    id
                                    entryId
                                    name
                                    polygons
                                }
                            } 
                        }
                    }    
                """
        result = schema.execute(query)
        # Check if center_longlat at the current record has
        # the same coordinates with the GraphQL query
        result_polygons = json.loads(
            result.data['allCountries']['edges'][0]['node']['polygons']
        )
        result_polygons_in_dict = json.loads(result_polygons)
        # The centerLonglat is JSONString, so it is needed to convert again
        # to the Python dictionary
        polygons_in_dict = json.loads(polygons_in_json)
        self.assertEqual(polygons_in_dict['coordinates'], result_polygons_in_dict[
            'coordinates'])
