from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileValidTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_check_file_valid(self):

        '''
        Test 1: Upload File
        '''

        with open('samples/check_file_valid_test_success.csv') as fp:
                res_file_upload = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'description': 'temp description',
                        'title': 'check_file_valid_test_success.csv',
                        })

        self.assertEquals(res_file_upload.status_code, 201, res_file_upload.json())
        self.assertIsNotNone(res_file_upload.json()['id'])

        '''
        Test 2: Check File is Valid
        '''

        res_check_file_valid = self.c.post(
            '/api/validate/check_file_valid/?format=json', 
            {
            'id': res_file_upload.json()['id'],
            },
            format='json'
            )

        self.assertEquals(res_check_file_valid.status_code, 200, res_check_file_valid.json())
        self.assertEquals(res_check_file_valid.json()['success'], 1)

        '''
        Test 3: Check File Validation results
        '''

        res_file_validate = self.c.post(
            '/api/validate/?format=json',
            {
            'id': res_file_upload.json()['id'],
            },
            format='json'
            )
        
        self.assertEquals(res_file_validate.status_code, 200, res_file_validate.json())
        self.assertIsNotNone(res_file_validate.json()['found_list'])
        self.assertIsNotNone(res_file_validate.json()['missing_list'])
        self.assertIsNotNone(res_file_validate.json()['summary'])
        
        

