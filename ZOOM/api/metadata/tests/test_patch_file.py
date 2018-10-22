from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from geodata.importer.country import CountryImport

class FilePatchTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_patch_file_valid(self):
        print('test_patch_file')
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

        res = self.c.post(
            '/api/metadata/sources/?format=json',
            {
                'name': 'The none',
            })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])
        id2= res.json()['id']

        '''
        Test 1: Upload file
        '''

        with open('samples/successful_upload_test.csv') as fp:
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

        '''
        Step 2: Patch file data
        '''

        patch_data = {
            "title": "Test1", 
            "description": "Description",
            "source": id2,
        }

        res_file_patch = self.c.patch(
                '/api/metadata/{}/?format=json'.format(res_file_upload.json()['id']),
                patch_data, format='json')
        
        # print res_file_patch.json()
        self.assertEquals(res_file_patch.status_code, 200, res_file_patch.json())

    
        '''
        Step2: Verify Patch file data
        '''
        res_file_patch_updated = self.c.get(
                '/api/metadata/{}/?format=json'.format(res_file_upload.json()['id']),format='json')

        self.assertEquals(res_file_patch_updated.status_code, 200, res_file_patch_updated.json())
        self.assertEquals(res_file_patch_updated.json()['title'], patch_data['title'])
        self.assertEquals(res_file_patch_updated.json()['description'], patch_data['description'])
        self.assertEquals(res_file_patch_updated.json()['source']['id'], patch_data['source'])

        '''
        Step 3: Patch file data Update
        '''

        patch_data = { 
            "title": "Test2", 
            "description": "Description2", 
            "location": 2
        }

        res_file_patch = self.c.patch(
                '/api/metadata/{}/?format=json'.format(res_file_upload.json()['id']),
                patch_data, format='json')
        
        # print res_file_patch.json()
        self.assertEquals(res_file_patch.status_code, 200, res_file_patch.json())
        
    
        '''
        Step4: Verify Patch file data update
        '''

        res_file_patch_updated = self.c.get(
                '/api/metadata/{}/?format=json'.format(res_file_upload.json()['id']), format='json')
        
        # print res_file_patch_updated.json()
        self.assertEquals(res_file_patch_updated.status_code, 200, res_file_patch_updated.json())
        self.assertEquals(res_file_patch_updated.json()['title'], patch_data['title'])
        self.assertEquals(res_file_patch_updated.json()['description'], patch_data['description'])
        self.assertEquals(res_file_patch_updated.json()['data_source']['name'], patch_data['data_source'])
        self.assertEquals(res_file_patch_updated.json()['tags'][0]['name'], patch_data['tags'][0])
        self.assertEquals(res_file_patch_updated.json()['status'], patch_data['status'])

