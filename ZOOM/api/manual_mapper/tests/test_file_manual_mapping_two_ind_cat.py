from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from geodata.importer.country import CountryImport
import json


class FileManualMappingTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_file_manual_mapping_two_measure_value(self):

        #Intialise countries
        #slow
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        '''
        Test 1: Upload file
        '''

        with open('samples/multiple_ind_cat.csv') as fp:
                res = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'title': 'temp title', 
                        'description': 'temp description', 
                        'file_name': 'measure_value string.csv',
                        })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])


        '''
        Test 2: Validate
        '''
        res_file_validate = self.c.post(
            '/api/validate/?format=json',
            {
            'file_id':res.json()['id'],
            }, format='json'
            )
        
        # print res_file_validate.json()['found_list']

        self.assertEquals(res_file_validate.status_code, 200, res_file_validate.json())
        self.assertIsNotNone(res_file_validate.json()['found_list'])
        self.assertIsNotNone(res_file_validate.json()['missing_list'])
        self.assertIsNotNone(res_file_validate.json()['summary'])

        '''
        Test 3: File Manual Mapping
        '''
        
        res_file_manual_mapping = self.c.post(
            '/api/manual-mapper/?format=json',
             {'dict': {'indicator': [], 'unit_of_measure': [], 'country': ['Country'], 'empty_indicator': 'Indicator value', 
             'measure_value': ['test'], 'date_value': ['Date'], 'source': [], 'other': [], 'indicator_category': ['Sex', 
             'Seen Transformers?', 'Seen Bambi?'], 'empty_unit_of_measure': {'test': 'Number'}} 
             'file_id': res.json()['id']}, format ='json'
            )
        # print res_file_manual_mapping
        
        self.assertEquals(res_file_manual_mapping.status_code, 200, res_file_manual_mapping.json())
        self.assertEquals(res_file_manual_mapping.json()['success'], 1)
