from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_post_file(self):

        '''
        Test 1: Upload file
        '''

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

        '''
        Test 2: delete File
        '''

        res_delete = self.c.delete('/api/file/{}/?format=json'.format(res.json()['id']))

        self.assertEquals(res_delete.status_code, 204)

        '''
        Test 3: Verify file deletion
        '''

        res_verify = self.c.get('/api/file/{}/?format=json'.format(res.json()['id']))

        self.assertEquals(res_verify.status_code, 404)


