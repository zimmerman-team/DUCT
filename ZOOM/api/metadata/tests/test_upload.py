from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from geodata.importer.country import CountryImport


class FileSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_source_file(self):
        res = self.c.post(
            '/api/metadata/sources/?format=json',
            {
                'name': 'The one',
            })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['file_source_id'])

        res_delete = self.c.delete('/api/metadata/sources/{}/?format=json'.format(res.json()['file_source_id']))
        self.assertEquals(res_delete.status_code, 204)

    def test_post_file(self):
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
        self.assertIsNotNone(res.json()['file_source_id'])
        file_source_id = res.json()['file_source_id']

        '''
        Test 1: Upload file
        '''

        with open('samples/successful_upload_test.csv') as fp:
            res = self.c.post(
                '/api/metadata/?format=json',
                {
                    'file': fp,
                    'title': 'temp title',
                    'description': 'temp description',
                    'contains_subnational_data': True,
                    'organisation': 'ZZ',
                    'maintainer': 'kieran',
                    'data_of_dataset': '2009-08-06',
                    'methodology': 'Testing',
                    'define_methodology': 'Really tesring',
                    'update_frequency': 'All the time',
                    'comments': 'Good stuff',
                    'accessibility': 'p',
                    'data_quality': 'good',
                    'number_of_rows': 200,
                    'file_types': 'csv',
                    'location': 1,
                    'source': file_source_id,
                })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['file_id'])

        '''
        Test 2: delete File
        '''

        res_delete = self.c.delete('/api/metadata/{}/?format=json'.format(res.json()['file_id']))

        self.assertEquals(res_delete.status_code, 204)

        '''
        Test 3: Verify file deletion
        '''

        #res_verify = self.c.get('/api/metadata/{}/?format=json'.format(res.json()['file_id']))

        #self.assertEquals(res_verify.status_code, 404)


