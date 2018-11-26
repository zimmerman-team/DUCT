from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileValidTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_check_file_valid_test_blank_lines(self):

        with open('samples/check_file_valid_test_blank_lines.csv') as fp:
                res_file_upload = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'title': 'temp title', 
                        'description': 'temp description', 
                        'file_name': 'check_file_valid_test_blank_lines.csv',
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
        
        # print res_check_file_valid

        self.assertEquals(res_check_file_valid.status_code, 200, res_check_file_valid.json())
        self.assertEquals(res_check_file_valid.json()['success'], 0)
        self.assertEquals(res_check_file_valid.json()['error'], "Files has blank lines or text at end of the file.")


