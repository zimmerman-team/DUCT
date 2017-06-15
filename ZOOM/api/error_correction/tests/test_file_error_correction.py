from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileErrorCorrectionTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_check_file_error_correction(self):

        '''
        Test 1: Upload File
        '''

        with open('samples/check_file_valid_test_success.csv') as fp:
                res_file_upload = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'title': 'temp title', 
                        'description': 'temp description', 
                        'file_name': 'check_file_valid_test_success.csv',
                        })

        self.assertEquals(res_file_upload.status_code, 201, res_file_upload.json())
        self.assertIsNotNone(res_file_upload.json()['id'])

        '''
        Test 2: Check File Error Correction
        '''

        res_file_error_correction = self.c.post('/api/error-correction/?format=json', 
            {            
            "file_id": res_file_upload.json()['id'],
            "start_pos": 0,
            "end_pos": 10,
            "type": "csv",
            "find_value": "",
            "filter_value": "",
            "filter_toggle": False,
            "replace_value": "",
            "replace_pressed": False
            },
            format='json'
            )

        print res_file_error_correction

        self.assertEquals(res_file_error_correction.status_code, 200, res_file_error_correction.json())
        self.assertIsNotNone(res_file_error_correction.json()['data_table'])
        self.assertIsNotNone(res_file_error_correction.json()['total_amount'])
