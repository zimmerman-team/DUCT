import json
import os

from django.test import TestCase

from geodata.importer.country import CountryImport
from gql.schema import schema
from gql.tests import factory


class MappingTestCase(TestCase):

    def setUp(self):
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()
        self.dummy_file_source = factory.FileSourceFactory(
            name='hello'
        )
        self.dummy_geolocation = factory.GeolocationFactory(
            tag='Austrlia',
            iso2='au',
            iso3='aus',
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
            file=os.path.abspath(
                'samples/two_mesure_values_num_date.csv')
        )

    def test_mapping_mutation(self):

        file_id = self.dummy_file.id

        EXTRA_INFORMATION = {
            'empty_entries': {
                'empty_indicator': 'Indicator value',
                'empty_geolocation': {
                    'value': '',
                    'type': ''},
                'empty_filter': '',
                'empty_value_format': {"2018": "Number", "2017": "Rate"},
                'empty_date': '2016'},
            'multi_mapped': {
                'column_heading': {'2018': 'date', '2017': 'date'},
                'column_values': {'2018': 'value', '2017': 'value'},
            },
            'point_based_info': {
                'coord': {
                    'lat': '',
                    'lon': ''},
                'subnational': '',
                'country': '',
                'type': '',
            }}

        input_json = {
            'metadata_id': file_id,
            'mapping_dict': {
                'indicator': [],
                'filters': [
                    'Source Type',
                    'Source'],
                'geolocation': ["Country or Area"],
                'date': [
                    "2018",
                    "2017"],
                'value_format': [],
                'value': [
                    "2018",
                    "2017"],
                'comment': [],
            },
            "filter_headings": {
                "Source Type": "Source",
                "Source": "Abbrv source"},
            'extra_information': EXTRA_INFORMATION}

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
