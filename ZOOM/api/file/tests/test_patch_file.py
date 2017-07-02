from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FilePatchTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_patch_file_valid(self):

        with open('samples/successful_file_patch_test.csv') as fp:
                res_file_upload = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'title': 'temp title', 
                        'description': 'temp description', 
                        'file_name': 'successful_file_patch_test.csv',
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

        '''
        Step 1: Patch file data
        '''

        patch_data = {
            "title": "Test1", 
            "description": "Description", 
            "tags": ["T"], 
            "data_source": "test_source_1",
            "authorised": False,
            "status": 1
        }

        res_file_patch = self.c.patch(
                '/api/file/{}/?format=json'.format(res_file_upload.json()['id']), 
                patch_data, format='json')
        
        # print res_file_patch.json()
        self.assertEquals(res_file_patch.status_code, 200, res_file_patch.json())

    
        '''
        Step2: Verify Patch file data
        '''
        res_file_patch_updated = self.c.get(
                '/api/file/{}/?format=json'.format(res_file_upload.json()['id']),format='json')
        
        self.assertEquals(res_file_patch_updated.status_code, 200, res_file_patch_updated.json())
        self.assertEquals(res_file_patch_updated.json()['title'], patch_data['title'])
        self.assertEquals(res_file_patch_updated.json()['description'], patch_data['description'])
        self.assertEquals(res_file_patch_updated.json()['data_source']['name'], patch_data['data_source'])
        self.assertEquals(res_file_patch_updated.json()['tags'][0]['name'], patch_data['tags'][0])
        self.assertEquals(res_file_patch_updated.json()['status'], patch_data['status'])
        
        '''
        Step 3: Patch file data Update
        '''

        patch_data = { 
            "title": "Test2", 
            "description": "Description2", 
            "tags": ["A"], 
            "data_source": "test_source_2",
            "authorised": True,
            "status": 2
        }

        res_file_patch = self.c.patch(
                '/api/file/{}/?format=json'.format(res_file_upload.json()['id']), 
                patch_data, format='json')
        
        # print res_file_patch.json()
        self.assertEquals(res_file_patch.status_code, 200, res_file_patch.json())
        
    
        '''
        Step4: Verify Patch file data update
        '''

        res_file_patch_updated = self.c.get(
                '/api/file/{}/?format=json'.format(res_file_upload.json()['id']), format='json')
        
        # print res_file_patch_updated.json()
        self.assertEquals(res_file_patch_updated.status_code, 200, res_file_patch_updated.json())
        self.assertEquals(res_file_patch_updated.json()['title'], patch_data['title'])
        self.assertEquals(res_file_patch_updated.json()['description'], patch_data['description'])
        self.assertEquals(res_file_patch_updated.json()['data_source']['name'], patch_data['data_source'])
        self.assertEquals(res_file_patch_updated.json()['tags'][0]['name'], patch_data['tags'][0])
        self.assertEquals(res_file_patch_updated.json()['status'], patch_data['status'])

