from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
import os
import json


class MappingTestCase(TestCase):

    def setUp(self):
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
            file=os.path.abspath("samples/point_based.csv")
        )

    def test_mapping_mutation(self):

        file_id = self.dummy_file.id

        EXTRA_INFORMATION = {
            'empty_entries': {
                'empty_indicator': 'Test pointbased',
                'empty_geolocation': {
                    'value': '',
                    'type': ''},
                'empty_filter': 'Default',
                'empty_value_format': {
                    'value format': 'Numeric'},
                'empty_date': '2016'},
            'multi_mapped': {
                'column_heading': {},
                'column_values': {},
            },
            'point_based_info': {
                'coord': {
                    'lat': 'Lat location 1',
                    'lon': 'Long location 1'},
                'subnational': '',
                'country': '',
                'type': '',
            }}

        input_json = {
            'metadata_id': file_id,
            'mapping_dict': {
                'indicator': [],
                'filters': [],
                'geolocation': ["Lat location 1", "Long location 1"],
                'date': [],
                'value_format': [],
                'value': ["new infections"],
                'comment': [],
            },
            "filter_headings": {"filters": "filters"},
            'extra_information': EXTRA_INFORMATION
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

        result = schema.execute(query, variable_values=query_input)
        self.assertEqual(result.errors, None)
