from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_post_file(self):

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

        res_check_file_valid = self.c.post(
            '/api/validate/check_file_valid/?format=json', 
            {
            'file_id': res_file_upload.json()['id'],
            },
            format='json'
            )

        self.assertEquals(res_check_file_valid.status_code, 200, res_check_file_valid.json())
        self.assertEquals(res_check_file_valid.json()['success'], 1)

