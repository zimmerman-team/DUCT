from django.test import TestCase
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from geodata.importer.country import CountryImport
from error_correction.utils import ERROR_CORRECTION_DICT
import json

class FileErrorCorrectionTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_check_file_error_correction(self):

        '''
        Test 1: Upload File
        '''

        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        '''
            Test 0: Upload Source
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
        with open('samples/check_file_valid_test_success.csv') as fp:
            res_file_upload = self.c.post(
                '/api/metadata/?format=json',
                {
                    'file': fp,
                    'title': 'temp title',
                    'description': 'temp description',
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

        self.assertEquals(res_file_upload.status_code, 201, res_file_upload.json())
        self.assertIsNotNone(res_file_upload.json()['id'])

        res_check_file_valid = self.c.post(
            '/api/validate/check_file_valid/?format=json',
            {
                'id': res_file_upload.json()['id'],
            },
            format='json'
        )

        self.assertEquals(res_check_file_valid.status_code, 200, res_check_file_valid.json())
        self.assertEquals(res_check_file_valid.json()['success'], 1)

        ERROR_CORRECTION_DICT['file_id'] = res_file_upload.json()['id']

        res_file_error_correction = self.c.post('/api/error-correction/?format=json', 
            ERROR_CORRECTION_DICT,
            format='json'
            )

        self.assertEquals(res_file_error_correction.status_code, 200, res_file_error_correction.json())
        self.assertIsNotNone(res_file_error_correction.json()['data_table'])
        self.assertIsNotNone(res_file_error_correction.json()['total_amount'])

        ERROR_CORRECTION_DICT['filter_column_heading'] = 'Element Code' #Column to filter on
        ERROR_CORRECTION_DICT['find_value'] = '31'
        ERROR_CORRECTION_DICT['replace_value'] = '41'
        ERROR_CORRECTION_DICT['filter_toggle'] = True
        ERROR_CORRECTION_DICT['replace_pressed'] = True

        res_file_error_correction = self.c.post('/api/error-correction/?format=json',
                                               ERROR_CORRECTION_DICT,
                                               format='json'
                                               )

        self.assertEquals(res_file_error_correction.status_code, 200, res_file_error_correction.json())
        self.assertIsNotNone(res_file_error_correction.json()['data_table'])
        self.assertIsNotNone(res_file_error_correction.json()['total_amount'])
        self.assertEquals(json.loads(res_file_error_correction.json()['data_table'])[0]['Element Code'], '41')

