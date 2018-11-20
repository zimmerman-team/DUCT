from gql.schema import schema
from django.test import TestCase
from gql.tests import factory
from mapping.models import Mapping
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
            file=os.path.abspath("samples/AIDSinfotest.csv")
        )

    def test_mapping_mutation(self):

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
        self.assertTrue(Mapping.objects.filter(data=input_json).exists())

    def test_mapping_query(self):

        self.test_mapping_mutation()  # we need to have a data in the database
        query = """{
            allMappings {
                edges {
                    node {
                        id
                        entryId
                        data
                    }
                }
            }
        }"""

        result = schema.execute(query)
        result_mapping_object = Mapping.objects.get(id=result.data
                                                    ['allMappings']['edges'][0]
                                                    ['node']['entryId'])
        self.assertTrue(result_mapping_object)
