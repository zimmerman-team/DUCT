from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
from geodata.models import Geolocation


class FiltersGeolocationsTestCase(TestCase):

    def setUp(self):
        dummy_country_one = factory.GeolocationFactory(tag='Albania',
                                                       iso2='al',
                                                       iso3='alb',
                                                       object_id=4,
                                                       content_type_id=15,
                                                       type='country'
                                                       )

        dummy_country_two = factory.GeolocationFactory(tag='Andora',
                                                       iso2='ad',
                                                       iso3='and',
                                                       object_id=7,
                                                       content_type_id=15,
                                                       type='country'
                                                       )

        dummy_country_three = factory.GeolocationFactory(tag='Bahamas',
                                                         iso2='bs',
                                                         iso3='bhs',
                                                         object_id=18,
                                                         content_type_id=15,
                                                         type='country'
                                                         )

        dummy_city_one = factory.GeolocationFactory(tag='london',
                                                    content_type_id=14,
                                                    type='city'
                                                    )

    def test_filter_first_geolocations(self):

        geolocation = Geolocation.objects.first()

        query = """
                {
                      allGeolocations(first:1) {
                         edges {
                          cursor
                          node {
                              id
                              tag
                            }
                          }
                      }
                }
                """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation.tag)

    def test_filter_last_geolocations(self):

        geolocation = Geolocation.objects.last()

        query = """
                {
                      allGeolocations(last:1) {
                            edges {
                                cursor
                                node {
                                    id
                                    tag
                                }
                            }
                      }
                }
                """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation.tag)

    def test_filter_tag_geolocations(self):

        geolocation = Geolocation.objects.filter(tag='Albania')

        query = """
                {
                      allGeolocations(tag:"Albania") {

                        edges {
                          cursor
                          node {
                                    id
                                    tag
                                }
                          }
                      }
                }
                """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)

    def test_filter_tag_icontains_geolocations(self):

        geolocation = Geolocation.objects.filter(tag__contains="lb")

        query = """
                        {
                              allGeolocations(tag_Icontains:"lb") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)

    def test_filter_tag_istartswith_geolocations(self):

        geolocation = Geolocation.objects.filter(tag__startswith="Al")

        query = """
                        {
                              allGeolocations(tag_Istartswith:"Al") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)

    def test_filter_tag_In_geolocations(self):

        geolocation = Geolocation.objects.filter(tag__in=["Albania", "Andora"])

        query = """
                        {
                              allGeolocations(tag_In:"Albania,Andora") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)
        self.assertEqual(result.data['allGeolocations']['edges'][1]['node']
                         ['tag'], geolocation[1].tag)

    def test_filter_objectId_geolocations(self):

        geolocation = Geolocation.objects.filter(object_id=4.0)

        query = """
                        {
                              allGeolocations(objectId:4.0) {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                            objectId
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['objectId'], geolocation[0].object_id)

    def test_filter_objectId_In_geolocations(self):

        geolocation = Geolocation.objects.filter(object_id__in=[4.0, 7.0])

        query = """
                        {
                              allGeolocations(objectId_In:"4,7") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                            objectId
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['objectId'], geolocation[0].object_id)
        self.assertEqual(result.data['allGeolocations']['edges'][1]['node']
                         ['objectId'], geolocation[1].object_id)

    def test_filter_type_geolocations(self):

        geolocation = Geolocation.objects.filter(type="city")

        query = """
                        {
                              allGeolocations(type:"city") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                            objectId
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)

    def test_filter_type_In_geolocations(self):

        geolocation = Geolocation.objects.filter(type__in=['country', 'city'])

        query = """
                        {
                              allGeolocations(type_In:"city,country") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                            objectId
                                        }
                                  }
                              }
                        }
                        """

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)
        self.assertEqual(result.data['allGeolocations']['edges'][1]['node']
                         ['tag'], geolocation[1].tag)
        self.assertEqual(result.data['allGeolocations']['edges'][2]['node']
                         ['tag'], geolocation[2].tag)
        self.assertEqual(result.data['allGeolocations']['edges'][3]['node']
                         ['tag'], geolocation[3].tag)

    def test_filter_entryId_geolocations(self):

        geolocation = Geolocation.objects.first()
        id = geolocation.id

        query = """
                        {
                              allGeolocations(entryId:%d) {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                            objectId
                                        }
                                  }
                              }
                        }
                        """ % id

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation.tag)

    def test_filter_entryId_In_geolocations(self):

        geolocation = Geolocation.objects.all()[:2]
        id_one = str(geolocation[0].id)
        id_two = str(geolocation[1].id)

        query = """
                        {
                              allGeolocations(entryId_In:"%s,%s") {

                                edges {
                                  cursor
                                  node {
                                            id
                                            tag
                                            objectId
                                        }
                                  }
                              }
                        }
                        """ % (id_one, id_two)

        result = schema.execute(query)
        self.assertEqual(result.data['allGeolocations']['edges'][0]['node']
                         ['tag'], geolocation[0].tag)
        self.assertEqual(result.data['allGeolocations']['edges'][1]['node']
                         ['tag'], geolocation[1].tag)
