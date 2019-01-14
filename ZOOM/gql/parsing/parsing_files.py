from gql.schema import schema
from metadata.models import FileSource, File
import json
import os
import glob


class Parsing():
    #please check path name, file_name, file source name
    # Adjust input_json_mapping

    def file_parsing(self):  # to be use this method to batch file processing
        path = os.path.abspath('samples/parsing_files/2019/*.csv')
        files = glob.glob(path)
        count = 0
        for full_path_file_name in files:
            file_name = 'parsing_files/2019/' + str(full_path_file_name).split(
                '/')[-1:][0]
            count += 1
            file_source_name = "2019samples" + str(count)
            Parsing.data_file_parsing(self,file_source_name=file_source_name,
                                   file_name=file_name)

    def data_file_parsing(self,file_source_name,file_name):

        file_source_query_input= {"input":{"name": file_source_name}}
        file_source_query = """
        mutation fileSource($input: FileSourceMutationInput!) {
            fileSource(input:$input) {
                                    name
            }
        }
        """
        schema.execute(file_source_query, 
                       variable_values=file_source_query_input)

        file_source_id = FileSource.objects.get(name=file_source_name).id
        location_id = 3
        file_mutation_input = """
                input: {
                    title: "test",
                    description: "test",
                    containsSubnationalData: true,
                    organisation: "test",
                    maintainer: "test",
                    dateOfDataset: "2009-01-01",
                    methodology: "test",
                    defineMethodology: "test",
                    updateFrequency: "test",
                    comments: "test",
                    accessibility: "p",
                    dataQuality: "test",
                    numberOfRows: 1,
                    fileTypes: "csv",
                    location: "%s",
                    source: "%s",
                    file: "%s"

                }""" % (location_id, file_source_id,file_name)

        file_mutation = """
                mutation file {
                    file(%s) {
                    id
                    description
                    containsSubnationalData
                    organisation
                    maintainer
                    dateOfDataset
                    methodology
                    defineMethodology
                    updateFrequency
                    comments
                    accessibility
                    dataQuality
                    numberOfRows
                    fileTypes
                    location
                    source
                    file
                    }
                }""" % file_mutation_input

        schema.execute(file_mutation)
        file_id = File.objects.get(file=os.path.abspath('samples/'+
                                                        file_name)).id

        EXTRA_INFORMATION = {
            'empty_entries':
                {
                    'empty_indicator': '',
                    'empty_geolocation': {'value': '', 'type': ''},

                    'empty_filter': '',
                    'empty_value_format': {},

                    'empty_date': ''
                },
            'multi_mapped':
                {
                    'column_heading': {},

                    'column_values': {},

                },
            'point_based_info':
                {
                    'coord': {'lat': '', 'lon': ''},
                    'subnational': '',
                    'country': '',
                    'type': '',

                }
        }

        input_json_mapping = {
            'metadata_id': file_id,
            'mapping_dict': {
                'indicator': ["indicator"],
                'geolocation': ["Country"],
                'date': ["date_value"],
                'value_format': ["unit_of_measure"],
                'value': ["measure_value"],
                'filters':["indicator_category"],
                'comment': [],
            },
            "filter_headings": {"indicator_category": "indicator_category"},
            "extra_information":EXTRA_INFORMATION
        }

        input_json_str = json.dumps(input_json_mapping)
        mapping_mutation_input = {"input": {"data": input_json_str}}
        mapping_mutation = """
                mutation mapping($input: MappingMutationInput!) {
                                            mapping(input: $input) {
                                                                id
                                                                data
                                        }
                }"""


        schema.execute(mapping_mutation,
                        variable_values=mapping_mutation_input)