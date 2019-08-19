from django.test import TestCase

from geodata.models import Geolocation
from gql.schema import schema
from gql.tests import factory


class FiltersGeolocationsTestCase(TestCase):
    def setUp(self):
        # so for the dummy geolocations we create
        # appropriate geolocation items
        alb = factory.CountryFactory(name='Albania', iso2='al', iso3='alb')
        andr = factory.CountryFactory(name='Andora', iso2='ad', iso3='and')
        bah = factory.CountryFactory(name='Bahamas', iso2='bs', iso3='bhs')
        amst = factory.CityFactory(name='Amsterdam')
        self.obj_id_1 = alb.id
        self.obj_id_2 = andr.id
        # Dummy geolocations
        factory.GeolocationFactory(tag='albania',
                                   iso2='al',
                                   iso3='alb',
                                   object_id=alb.id,
                                   content_type_id=16,
                                   type='country')
        factory.GeolocationFactory(tag='andora',
                                   iso2='ad',
                                   iso3='and',
                                   object_id=andr.id,
                                   content_type_id=16,
                                   type='country')
        factory.GeolocationFactory(tag='bahamas',
                                   iso2='bs',
                                   iso3='bhs',
                                   object_id=bah.id,
                                   content_type_id=16,
                                   type='country')
        factory.GeolocationFactory(tag='amsterdam',
                                   object_id=amst.id,
                                   content_type_id=15,
                                   type='city')

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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation.tag)

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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation.tag)

    def test_filter_tag_geolocations(self):
        geolocation = Geolocation.objects.filter(tag='albania')
        query = """
        {
            allGeolocations(tag:"albania") {
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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)

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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)

    def test_filter_tag_istartswith_geolocations(self):
        geolocation = Geolocation.objects.filter(tag__startswith="al")
        query = """
        {
            allGeolocations(tag_Istartswith:"al") {
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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)

    def test_filter_tag_In_geolocations(self):
        geolocation = Geolocation.objects.filter(tag__in=["albania", "andora"])
        query = """
        {
            allGeolocations(tag_In:"albania,andora") {
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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)
        self.assertEqual(
            result.data['allGeolocations']['edges'][1]['node']['tag'],
            geolocation[1].tag)

    def test_filter_objectId_geolocations(self):
        geolocation = Geolocation.objects.filter(object_id=self.obj_id_1)
        query = """
                query geolocations($object_id_str: String!){
                    allGeolocations(objectId_In: $object_id_str) {
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

        object_id_str = {"object_id_str": str(self.obj_id_1) + ','}

        result = schema.execute(query, variable_values=object_id_str)

        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['objectId'],
            geolocation[0].object_id)

    def test_filter_objectId_In_geolocations(self):
        geolocation = Geolocation.objects.filter(
            object_id__in=[self.obj_id_1, self.obj_id_2])
        query = """
        query geolocations($object_id_str: String!){
            allGeolocations(objectId_In: $object_id_str) {
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

        object_id_str = {
            "object_id_str": str(self.obj_id_1) + ',' + str(self.obj_id_2)
        }

        result = schema.execute(query, variable_values=object_id_str)
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['objectId'],
            geolocation[0].object_id)
        self.assertEqual(
            result.data['allGeolocations']['edges'][1]['node']['objectId'],
            geolocation[1].object_id)

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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)

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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)
        self.assertEqual(
            result.data['allGeolocations']['edges'][1]['node']['tag'],
            geolocation[1].tag)
        self.assertEqual(
            result.data['allGeolocations']['edges'][2]['node']['tag'],
            geolocation[2].tag)
        self.assertEqual(
            result.data['allGeolocations']['edges'][3]['node']['tag'],
            geolocation[3].tag)

    def test_filter_entryId_geolocations(self):
        geolocation = Geolocation.objects.first()
        geolocation_id = geolocation.id
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
        """ % geolocation_id

        result = schema.execute(query)
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation.tag)

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
        self.assertEqual(
            result.data['allGeolocations']['edges'][0]['node']['tag'],
            geolocation[0].tag)
        self.assertEqual(
            result.data['allGeolocations']['edges'][1]['node']['tag'],
            geolocation[1].tag)
