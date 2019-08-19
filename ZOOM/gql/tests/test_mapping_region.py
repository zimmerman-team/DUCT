import json
import os

from django.test import TestCase

from geodata.importer.region import RegionImport
from gql.schema import schema
from gql.tests import factory
from mapping.mapper import begin_mapping


class MappingTestCase(TestCase):
    def setUp(self):
        # initialize  Region
        ri = RegionImport()
        ri.update_region_center()

        # creating dummy objects for testing
        self.dummy_file_source = factory.FileSourceFactory(
            name='dummy_file_source')
        region = factory.RegionFactory(name='central asia')
        self.dummy_geolocation = factory.GeolocationFactory(
            tag='central asia',
            object_id=region.id,
            content_type_id=19,
            type='region')
        self.dummy_file = factory.FileFactory(
            title="Region",
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
            file=os.path.abspath("samples/region.csv"))

    def test_mapping_mutation(self):

        file_id = self.dummy_file.id

        EXTRA_INFORMATION = {
            'empty_entries': {
                'empty_indicator': 'Test Region',
                'empty_geolocation': {
                    'value': '',
                    'type': ''
                },
                'empty_filter': 'Default',
                'empty_value_format': {
                    'value format': 'Numeric'
                },
                'empty_date': ''
            },
            'multi_mapped': {
                'column_heading': {},
                'column_values': {},
            },
            'point_based_info': {
                'coord': {
                    'lat': '',
                    'lon': ''
                },
                'subnational': '',
                'country': '',
                'type': '',
            }
        }

        input_json = {
            'metadata_id': file_id,
            'mapping_dict': {
                'indicator': [],
                'geolocation': ["Region"],
                'date': ['datez'],
                'value_format': [],
                'value': ["new infections"],
                'comment': [],
            },
            "filter_headings": {
                "filters": "filters"
            },
            'extra_information': EXTRA_INFORMATION
        }

        result = begin_mapping(input_json)
        self.assertEqual(result['success'], 1)

        # input_json_str = json.dumps(input_json)
        # query_input = {"input": {"data": input_json_str}}
        # query = """
        # mutation mapping($input: MappingMutationInput!) {
        #                             mapping(input: $input) {
        #                                                 id
        #                                                 data
        #                         }
        # }"""

        # result = schema.execute(query, variable_values=query_input)
        # self.assertEqual(result.errors, None)
