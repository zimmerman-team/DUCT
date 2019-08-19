import os

from django.db.models import Avg, Count, Max, Min, Sum
from django.test import TestCase

from geodata.importer.country import CountryImport
from gql.schema import schema
from gql.tests import factory
from indicator.models import Datapoints
from mapping.mapper import begin_mapping


class DatapointsAggregationTestCase(TestCase):
    def setUp(self):
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        self.dummy_file_source = factory.FileSourceFactory(
            name='dummy_file_source')
        self.dummy_geolocation = factory.GeolocationFactory(tag='Albania',
                                                            iso2='al',
                                                            iso3='alb',
                                                            object_id=4,
                                                            content_type_id=15,
                                                            type='country')
        self.dummy_file = factory.FileFactory(
            title="test",
            description="test",
            contains_subnational_data=True,
            organisation="test",
            maintainer="test",
            date_of_dataset="2009-01-01",
            methodology="test",
            define_methodology="test",
            update_frequency="test",
            comments="test",
            accessibility="p",
            data_quality="test",
            number_of_rows=1,
            file_types="csv",
            location=self.dummy_geolocation,
            source=self.dummy_file_source,
            file=os.path.abspath("samples/AIDSinfotest.csv"))

        file_id = self.dummy_file.id

        input_json = {
            'metadata_id': file_id,
            'filter_headings': {
                "Subgroup": "Subgroup"
            },
            "extra_information": {
                "empty_entries": {
                    "empty_indicator": '',
                    "empty_geolocation": {
                        "value": '',
                        "type": ''
                    },
                    "empty_filter": '',
                    "empty_value_format": {},
                    "empty_date": ''
                },
                "multi_mapped": {
                    "column_heading": {},
                    "column_values": {}
                },
                "point_based_info": {
                    "coord": {
                        "lat": '',
                        "lon": ''
                    },
                    "subnational": '',
                    "country": '',
                    "type": ''
                }
            },
            'mapping_dict': {
                "indicator": ["Indicator"],
                "value_format": ["Unit"],
                "geolocation": ["Area"],
                "value": ["Data Value"],
                "date": ["Time Period"],
                "comment": ["Source"],
                "filters": ["Subgroup"]
            }
        }

        begin_mapping(input_json)

        # input_json_str = json.dumps(input_json)
        # so this query call based mapping doesn't seem to work very properly
        # so we comment this out for now and will adress this later
        # but for the data just to be mapped out we'll just use the mapping
        # function itself here
        # query_input = {"input": {"data": input_json_str}}
        # query = """
        # mutation mapping($input: MappingMutationInput!) {
        #                             mapping(input: $input) {
        #                                                 id
        #                                                 data
        #                         }
        # }"""
        #
        # schema.execute(query, variable_values=query_input)
        # time.sleep(10)

    def test_datapoints_aggregation_parm_groupBy_missing(self):

        query = """
        {
            datapointsAggregation(orderBy:[
            "indicatorName"],aggregation: ["Sum(value)"]) {
                indicatorName
                value
            }
        }"""
        result = schema.execute(query)
        self.assertEqual(result.errors[0].message, "'groupBy'")

    def test_datapoints_aggregation_parm_orderBy_missing(self):

        query = """{
        datapointsAggregation(groupBy: ["indicatorName"],aggregation: ["Sum(value)"]) {
            indicatorName
            value
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.errors[0].message, "'orderBy'")

    def test_datapoints_aggregation_parm_aggregation_missing(self):

        query = """{
        datapointsAggregation(groupBy: ["indicatorName"],orderBy:["indicatorName"]) {
            indicatorName
            value
            }
        }
        """

        result = schema.execute(query)
        self.assertEqual(result.errors[0].message, "'aggregation'")

    def test_datapoints_aggregation_parm_pass(self):

        query = """{
                datapointsAggregation(groupBy: ["indicatorName"],orderBy:[
                "indicatorName"], aggregation:["Sum(value)"]) {
                    indicatorName
                    value
                    }
                }
                """

        result = schema.execute(query)
        self.assertIsNone(result.errors)

    def test_datapoints_aggregation_Avg_Sum_Min_Max_Count(self):

        query = """{
        datapointsAggregation(groupBy: ["indicatorName"], orderBy: [
            "indicatorName"], aggregation: ["Avg(value)"]) {
                indicatorName
                geolocationTag
                value
            }
        }"""

        result = schema.execute(query)
        self.assertIsNone(result.errors)
        val = Datapoints.objects.filter(
            indicator__name='people living with '
            'hiv').order_by('indicator__name').aggregate(Avg('value'))
        self.assertEqual(result.data['datapointsAggregation'][0]['value'],
                         val['value__avg'])

        # testing for Sum

        query = """{
                datapointsAggregation(groupBy: ["indicatorName"], orderBy: [
                    "indicatorName"], aggregation: ["Sum(value)"]) {
                        indicatorName
                        geolocationTag
                        value
                    }
                }"""

        result = schema.execute(query)
        self.assertIsNone(result.errors)
        val = Datapoints.objects.filter(
            indicator__name='people living with '
            'hiv').order_by('indicator__name').aggregate(Sum('value'))
        self.assertEqual(result.data['datapointsAggregation'][0]['value'],
                         val['value__sum'])

        # testing for Minimum

        query = """{
                datapointsAggregation(groupBy: ["indicatorName"], orderBy: [
                    "indicatorName"], aggregation: ["Min(value)"]) {
                        indicatorName
                        geolocationTag
                        value
                    }
                }"""

        result = schema.execute(query)
        self.assertIsNone(result.errors)
        val = Datapoints.objects.filter(
            indicator__name='people living with '
            'hiv').order_by('indicator__name').aggregate(Min('value'))
        self.assertEqual(result.data['datapointsAggregation'][0]['value'],
                         val['value__min'])

        # testing Maximum

        query = """{
                datapointsAggregation(groupBy: ["indicatorName"], orderBy: [
                    "indicatorName"], aggregation: ["Max(value)"]) {
                        indicatorName
                        geolocationTag
                        value
                    }
                }"""

        result = schema.execute(query)
        self.assertIsNone(result.errors)
        val = Datapoints.objects.filter(
            indicator__name='people living with '
            'hiv').order_by('indicator__name').aggregate(Max('value'))
        self.assertEqual(result.data['datapointsAggregation'][0]['value'],
                         val['value__max'])

        # testing for Count

        query = """{
                datapointsAggregation(groupBy: ["indicatorName"], orderBy: [
                    "indicatorName"], aggregation: ["Count(value)"]) {
                        indicatorName
                        geolocationTag
                        value
                    }
                }"""

        result = schema.execute(query)
        self.assertIsNone(result.errors)
        val = Datapoints.objects.filter(
            indicator__name='people living with '
            'hiv').order_by('indicator__name').aggregate(Count('value'))
        self.assertEqual(result.data['datapointsAggregation'][0]['value'],
                         val['value__count'])

    def test_datapoints_aggregation_geolocationTag_In(self):

        query = """{
                datapointsAggregation(groupBy:["indicatorName","geolocationTag"],orderBy:["indicatorName"],aggregation:["Sum(value)"],
                geolocationTag_In: ["mongolia","lesotho"] ) {
                    indicatorName
                    value
                    geolocationTag
                    }
                }"""
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        countries = Datapoints.objects.values(
            'indicator__name',
            'geolocation__tag').annotate(Sum('value')).filter(
                geolocation__tag__in=['lesotho', 'mongolia']).order_by(
                    'indicator__name')

        self.assertEqual(len(countries),
                         len(result.data['datapointsAggregation']))
        i = 0
        while i < len(countries):
            self.assertEqual(
                result.data['datapointsAggregation'][i]['geolocationTag'],
                countries[i]['geolocation__tag'])
            i += 1

    def test_datapoints_aggregation_geolocationIso2_In(self):
        query = """{
                datapointsAggregation(groupBy:["indicatorName",
                "geolocationIso2"],orderBy:["indicatorName"],aggregation:["Sum(value)"],
                geolocationIso2_In: ["mn","ls"] ) {
                    indicatorName
                    value
                    geolocationIso2
                    }
                }"""
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        countries = Datapoints.objects.values(
            'indicator__name',
            'geolocation__iso2').annotate(Sum('value')).filter(
                geolocation__iso2__in=['mn', 'ls']).order_by('indicator__name')

        self.assertEqual(len(countries),
                         len(result.data['datapointsAggregation']))
        i = 0
        while i < len(countries):
            self.assertEqual(
                result.data['datapointsAggregation'][i]['geolocationIso2'],
                countries[i]['geolocation__iso2'])
            i += 1

    def test_datapoints_aggregation_geolocationIso3_In(self):

        query = """{
                datapointsAggregation(groupBy:["indicatorName",
                "geolocationIso3"],orderBy:["indicatorName"],aggregation:[
                "Sum(value)"],
                geolocationIso3_In: ["mng","lso"] ) {
                    indicatorName
                    value
                    geolocationIso3
                    }
                }"""
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        countries = Datapoints.objects.values(
            'indicator__name',
            'geolocation__iso3').annotate(Sum('value')).filter(
                geolocation__iso3__in=['mng', 'lso']).order_by(
                    'indicator__name')

        self.assertEqual(len(countries),
                         len(result.data['datapointsAggregation']))
        i = 0
        while i < len(countries):
            self.assertEqual(
                result.data['datapointsAggregation'][i]['geolocationIso3'],
                countries[i]['geolocation__iso3'])
            i += 1

    def test_datapoints_aggregation_geolocationObjectId_In(self):

        query = """{
                datapointsAggregation(groupBy:["indicatorName",
                "geolocationObjectId"],orderBy:["indicatorName"],aggregation:[
                "Sum(value)"],geolocationObjectId_In: ["126","149"] ) {
                    indicatorName
                    value
                    geolocationObjectId
                    }
                }"""
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        countries = Datapoints.objects.values(
            'indicator__name',
            'geolocation__object_id').annotate(Sum('value')).filter(
                geolocation__object_id__in=['126', '149']).order_by(
                    'indicator__name')

        self.assertEqual(len(countries),
                         len(result.data['datapointsAggregation']))
        i = 0
        while i < len(countries):
            self.assertEqual(
                result.data['datapointsAggregation'][i]['geolocationObjectId'],
                countries[i]['geolocation__object_id'])
            i += 1

    def test_datapoints_aggregation_geolocationType_In(self):

        query = """{
                    datapointsAggregation(groupBy:["indicatorName",
                    "geolocationType"],orderBy:["indicatorName"],aggregation:[
                    "Sum(value)"],geolocationType_In: ["subnational",
                    "country"] ) {
                        indicatorName
                        value
                        geolocationType
                        }
                    }"""
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        countries = Datapoints.objects.values(
            'indicator__name',
            'geolocation__type').annotate(Sum('value')).filter(
                geolocation__type__in=['subnational', 'country']).order_by(
                    'indicator__name')

        self.assertEqual(len(countries),
                         len(result.data['datapointsAggregation']))
        i = 0
        while i < len(countries):
            self.assertEqual(
                result.data['datapointsAggregation'][i]['geolocationType'],
                countries[i]['geolocation__type'])
            i += 1
