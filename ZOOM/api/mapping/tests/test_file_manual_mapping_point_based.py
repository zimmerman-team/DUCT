from django.test import TestCase
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from geodata.importer.region import RegionImport
from geodata.importer.country import CountryImport
from geodata.importer.subnational import SubnationalImport
from indicator.models import MAPPING_DICT


class FileManualMappingTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_file_manual_mapping(self):
        # Intialise countries
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        si = SubnationalImport()
        si.update_polygon()

        '''
        Test 0: Upload file
        '''

        res = self.c.post(
            '/api/metadata/sources/?format=json',
            {
                'name': 'The one',
            })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])
        id = res.json()['id']

        '''
        Test 1: Upload file
        '''

        with open('samples/point_based.csv') as fp:
            res = self.c.post(
                '/api/metadata/?format=json',
                {
                    'file': fp,
                    'description': 'temp description',
                    'title': 'AIDSinfotest.csv',
                    'contains_subnational_data': True,
                    'organisation': 'ZZ',
                    'maintainer': 'kieran',
                    'date_of_dataset': '2009-08-06',
                    'methodology': 'Testing',
                    'define_methodology': 'Really tesring',
                    'update_frequency': 'All the time',
                    'comments': 'Good stuff',
                    'accessibility': 'p',
                    'data_quality': 'good',
                    'number_of_rows': 200,
                    'file_types': 'csv',
                    'location': 1,
                    'source': id,
                })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])

        '''
        Test 2: Validate
        '''
        res_file_validate = self.c.post(
            '/api/validate/?format=json',
            {
                'id': res.json()['id'],
            }, format='json'
        )

        # print res_file_validate.json()['found_list']

        self.assertEquals(res_file_validate.status_code, 200, res_file_validate.json())
        self.assertIsNotNone(res_file_validate.json()['found_list'])
        self.assertIsNotNone(res_file_validate.json()['missing_list'])
        self.assertIsNotNone(res_file_validate.json()['summary'])

        '''
        Test 3: File Manual Mapping
        '''
        mapping_template = MAPPING_DICT
        MAPPING_DICT['metadata_id'] = res.json()['id']
        MAPPING_DICT['mapping_dict']['geolocation'] = ['Lat location 1', 'Long location 1']
        MAPPING_DICT['mapping_dict']['value'] = ['new infections']
        MAPPING_DICT['filter_headings'] = {'filters': 'filters'}
        MAPPING_DICT['extra_information']['empty_entries']['empty_indicator'] = 'Test pointbased'
        MAPPING_DICT['extra_information']['empty_entries']['empty_filter'] = 'Default',
        MAPPING_DICT['extra_information']['empty_entries']['empty_value_format'] = {'value_format': 'Numeric'},
        MAPPING_DICT['extra_information']['empty_entries']['empty_date'] = '2016'
        MAPPING_DICT['extra_information']['point_based_info']['coord']['lat'] = 'Lat location 1'
        MAPPING_DICT['extra_information']['point_based_info']['coord']['lon'] = 'Long location 1'

        # **manual_mapping_data,
        res_file_manual_mapping = self.c.post(
            '/api/mapping/?format=json',
            MAPPING_DICT,
            format='json'
        )

        '''
        {
                'id': res.json()['id'],
                'dict': {
                    'indicator': [],
                    'value_format': [],
                    'geolocation': [
                        'Lat location 1',
                        'Long location 1',
                    ],
                    'value': [
                        'new infections'
                    ],
                    'date': [],
                    'comment': [],
                    'filters': [],
                    'headings': {
                        'filters': 'filters'
                    },
                    'empty_indicator': 'Test region',
                    'empty_geolocation_type': '',
                    'empty_filter': 'Default',
                    'empty_value_format': {'value_format': 'Numeric'},
                    'empty_date': '2016',
                    'additional_geolocation_info': {'coord': {'lat': 'Lat location 1',
                              'lon': 'Long location 1'}}
                },
            }
        '''

        self.assertEquals(res_file_manual_mapping.status_code, 200, res_file_manual_mapping.json())
        self.assertEquals(res_file_manual_mapping.json()['success'], 1)
