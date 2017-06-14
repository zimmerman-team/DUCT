from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_post_file(self):

        with open('samples/successful_upload_test.csv') as fp:
                res = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'title': 'temp title', 
                        'description': 'temp description', 
                        'file_name': 'successful_upload_test.csv',
                        })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])
