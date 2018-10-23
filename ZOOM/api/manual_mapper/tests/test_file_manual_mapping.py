from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from geodata.importer.country import CountryImport


class FileManualMappingTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_file_manual_mapping(self):

        #Intialise countries
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        '''
        Test 1: Upload file
        '''

        with open('samples/AIDSinfotest.csv') as fp:
                res = self.c.post(
                        '/api/file/?format=json', 
                        {
                        'file': fp,
                        'title': 'temp title', 
                        'description': 'temp description', 
                        'file_name': 'AIDSinfotest.csv',
                        })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])


        '''
        Test 2: Validate
        '''
        res_file_validate = self.c.post(
            '/api/validate/?format=json',
            {
            'id': res.json()['id'],
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
        manual_mapping_data = {
            "id": res.json()['id'],
            "dict": {
                "indicator": [
                    "Indicator"
                ],
                "unit_of_measure": [
                    "Unit"
                ],
                "country": [
                    "Area ID"
                ],
                "measure_value": [
                    "Data Value"
                ],
                "date_value": [
                    "Time Period"
                ],
                "source": [
                    "Source"
                ],
                "other": [
                    "Footnotes"
                ],
                "indicator_category": [
                    "Subgroup"
                ]
            }
        }
        # print manual_mapping_data

        res_file_manual_mapping = self.c.post(
            '/api/manual-mapper/?format=json', 
            {
            "id": res.json()['id'],
            "dict": {
                "indicator": [
                    "Indicator"
                ],
                "unit_of_measure": [
                    "Unit"
                ],
                "country": [
                    "Area ID"
                ],
                "measure_value": [
                    "Data Value"
                ],
                "date_value": [
                    "Time Period"
                ],
                "source": [ 
                    "Source"
                ],
                "other": [
                    "Footnotes"
                ],
                "indicator_category": [
                    "Subgroup"
                ]
            } },
            format='json'
            )
        
        # print res_file_manual_mapping
        
        self.assertEquals(res_file_manual_mapping.status_code, 200, res_file_manual_mapping.json())
        self.assertEquals(res_file_manual_mapping.json()['success'], 1)
