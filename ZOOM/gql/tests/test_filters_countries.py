from django.test import TestCase

from geodata.models import Country
from gql.schema import schema
from gql.tests import factory


class FiltersCountriesTestCase(TestCase):

    def setUp(self):
        # Dummy Country
        factory.CountryFactory(name='Albania', iso2='al', iso3='alb')
        factory.CountryFactory(name='Andora', iso2='ad', iso3='and')
        factory.CountryFactory(name='Bahamas', iso2='bs', iso3='bhs')
        factory.CountryFactory(name='Australia', iso2='au', iso3='aus')

    def test_filter_first_countries(self):
        country = Country.objects.first()
        query = """
        {
            allCountries(first:1) {
                    edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(
            result.data['allCountries']['edges'][0]['node']['name'],
            country.name)

    def test_filter_last_countries(self):
        country = Country.objects.last()
        query = """
        {
            allCountries(last:1) {
                edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(
            result.data['allCountries']['edges'][0]['node']['name'],
            country.name)

    def test_filter_name_countries(self):
        country = Country.objects.filter(name='Albania')
        query = """
        {
            allCountries(name:"Albania") {
                edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(
            result.data['allCountries']['edges'][0]['node']['name'],
            country[0].name)

    def test_filter_name_icontains_countries(self):
        country = Country.objects.filter(name__contains="lb")
        query = """
        {
            allCountries(name_Icontains:"lb") {
                edges {
                    cursor
                    node {
                        id
                         name
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(
            result.data['allCountries']['edges'][0]['node']['name'],
            country[0].name)

    def test_filter_tag_istartswith_countries(self):
        country = Country.objects.filter(name__startswith="Al")
        query = """
        {
            allCountries(name_Istartswith:"Al") {
                edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['name'], country[0].name)

    def test_filter_name_In_countries(self):

        country = Country.objects.filter(name__in=["Albania", "Andora"])

        query = """
        {
            allCountries(name_In:"Albania,Andora") {
                edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['name'], country[0].name)
        self.assertEqual(result.data['allCountries']['edges'][1]['node']
                         ['name'], country[1].name)

    def test_filter_iso2_countries(self):

        country = Country.objects.filter(iso2='al')

        query = """
        {
            allCountries(iso2:"al") {
                edges {
                    cursor
                    node {
                        id
                        iso2
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso2'], country[0].iso2)

    def test_filter_iso2_icontains_countries(self):
        country = Country.objects.filter(iso2__contains='al')
        query = """
        {
            allCountries(iso2_Icontains:"al") {
                edges {
                    cursor
                    node {
                        id
                        iso2
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso2'], country[0].iso2)

    def test_filter_iso2_istartswith_countries(self):
        country = Country.objects.filter(iso2__istartswith='al')
        query = """
        {
            allCountries(iso2_Istartswith:"al") {
                edges {
                    cursor
                    node {
                        id
                        iso2
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso2'], country[0].iso2)

    def test_filter_iso2_In_countries(self):
        country = Country.objects.filter(iso2__in=['al', 'bs'])
        query = """
        {
            allCountries(iso2_In:"al,bs") {
                edges {
                    cursor
                    node {
                        id
                        iso2
                    }
                }
            }
        }
         """

        result = schema.execute(query)

        country_list = [country[0].iso2, country[1].iso2].sort()

        result_list = [result.data['allCountries']['edges'][0]['node']
                         ['iso2'],
                       result.data['allCountries']['edges'][1]['node']
                       ['iso2']].sort()

        self.assertTrue(country_list == result_list)

    def test_filter_iso3_countries(self):
        country = Country.objects.filter(iso3='alb')
        query = """
        {
            allCountries(iso3:"alb") {
                edges {
                    cursor
                    node {
                        id
                        iso3
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso3'], country[0].iso3)

    def test_filter_iso3_icontains_countries(self):
        country = Country.objects.filter(iso3__contains='al')
        query = """
        {
            allCountries(iso3_Icontains:"al") {
                edges {
                    cursor
                    node {
                        id
                        iso3
                    }
                }
            }
        }
         """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso3'], country[0].iso3)

    def test_filter_iso3_istartswith_countries(self):
        country = Country.objects.filter(iso2__istartswith='al')
        query = """
        {
            allCountries(iso3_Istartswith:"al") {
                edges {
                    cursor
                    node {
                        id
                        iso3
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso3'], country[0].iso3)

    def test_filter_iso3_In_countries(self):
        country = Country.objects.filter(iso3__in=['alb', 'aus'])
        query = """
        {
            allCountries(iso3_In:"alb,aus") {
                edges {
                    cursor
                    node {
                        id
                        iso3
                    }
                }
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['iso3'], country[0].iso3)

        self.assertEqual(result.data['allCountries']['edges'][1]['node']
                         ['iso3'], country[1].iso3)

    def test_filter_entryId_countries(self):
        country = Country.objects.first()
        country_id = country.id
        query = """
        {
            allCountries(entryId:%d) {
                edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """ % country_id

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['name'], country.name)

    def test_filter_entryId_In_countries(self):
        country = Country.objects.all()[:2]
        country_id_one = str(country[0].id)
        country_id_two = str(country[1].id)
        query = """
        {
            allCountries(entryId_In:"%s,%s") {
                edges {
                    cursor
                    node {
                        id
                        name
                    }
                }
            }
        }
        """ % (country_id_one, country_id_two)

        result = schema.execute(query)
        self.assertEqual(result.data['allCountries']['edges'][0]['node']
                         ['name'], country[0].name)
        self.assertEqual(result.data['allCountries']['edges'][1]['node']
                         ['name'], country[1].name)
