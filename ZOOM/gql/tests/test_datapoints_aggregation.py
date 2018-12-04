from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
from indicator.models import Datapoints
from django.db.models import Avg, Sum, Min, Max, Count
from geodata.importer.country import CountryImport
import os
import json


class MappingTestCase(TestCase):

    def setUp(self):
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        self.dummy_file_source = factory.FileSourceFactory(
            name='dummy_file_source'
        )
        self.dummy_geolocation = factory.GeolocationFactory(
            tag='Albania',
            iso2='al',
            iso3='alb',
            object_id=4,
            content_type_id=15,
            type='country'
        )
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
            file=os.path.abspath("samples/AIDSinfotest.csv")
        )

        file_id = self.dummy_file.id

        input_json = {
            'metadata_id': file_id,
            'mapping_dict': {
                "indicator": ["Indicator"],
                "value_format": ["Unit"],
                "geolocation": ["Area"],
                "value": ["Data Value"],
                "date": ["Time Period"],
                "comment": ["Source"],
                "filters": ["Subgroup"]
            },
            'filter_headings': {"Subgroup": "Subgroup"},
        }

        input_json_str = json.dumps(input_json)
        query_input = {"input": {"data": input_json_str}}
        query = """
        mutation mapping($input: MappingMutationInput!) {
                                    mapping(input: $input) {
                                                        id
                                                        data
                                }
        }"""

        schema.execute(query, variable_values=query_input)

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
        val = Datapoints.objects.filter(indicator__name='People living with '
                                        'HIV').aggregate(Avg('value'))
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
        val = Datapoints.objects.filter(indicator__name='People living with '
                                                        'HIV').aggregate(
            Sum('value'))
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
        val = Datapoints.objects.filter(indicator__name='People living with '
                                                        'HIV').aggregate(
            Min('value'))
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
        val = Datapoints.objects.filter(indicator__name='People living with '
                                                        'HIV').aggregate(
            Max('value'))
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
        val = Datapoints.objects.filter(indicator__name='People living with '
                                                        'HIV').aggregate(
            Count('value'))
        self.assertEqual(result.data['datapointsAggregation'][0]['value'],
                         val['value__count'])
