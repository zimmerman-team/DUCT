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

