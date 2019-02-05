from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from geodata.importer.country import CountryImport


class FileValidTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_check_file_valid(self):
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        """
        Test 0: Add source
        """
        res = self.c.post(
            '/api/metadata/sources/?format=json',
            {
                'name': 'The one',
            })

        self.assertEquals(res.status_code, 201, res.json())
        self.assertIsNotNone(res.json()['id'])
        id = res.json()['id']

        """
        Test 1: Upload file
        """
        with open('samples/check_file_valid_test_success.csv') as fp:
            res_file_upload = self.c.post(
                '/api/metadata/?format=json',
                {
                    'file': fp,
                    'title': 'temp title',
                    'description': 'temp description',
                    'contains_subnational_data': True,
                    'organisation': 'ZZ',
                    'maintainer': 'tester',
                    'date_of_dataset': '2009-08-06',
                    'methodology': 'Testing',
                    'define_methodology': 'Really testing',
                    'update_frequency': 'All the time',
                    'comments': 'Good stuff',
                    'accessibility': 'p',
                    'data_quality': 'good',
                    'number_of_rows': 200,
                    'file_types': 'csv',
                    'location': 1,
                    'source': id,
                })

        self.assertEquals(res_file_upload.status_code, 201,
                          res_file_upload.json())
        self.assertIsNotNone(res_file_upload.json()['id'])

        '''
        Test 3: Check File is Valid
        '''

        res_check_file_valid = self.c.post(
            '/api/validate/check_file_valid/?format=json',
            {
                'id': res_file_upload.json()['id'],
            },
            format='json'
        )

        self.assertEquals(res_check_file_valid.status_code, 200,
                          res_check_file_valid.json())
        self.assertEquals(res_check_file_valid.json()['success'], 1)

        '''
        Test 4: Check File Validation results
        '''

        res_file_validate = self.c.post(
            '/api/validate/?format=json',
            {
                'id': res_file_upload.json()['id'],
            },
            format='json'
        )

        self.assertEquals(res_file_validate.status_code, 200,
                          res_file_validate.json())
        self.assertIsNotNone(res_file_validate.json()['found_list'])
        self.assertIsNotNone(res_file_validate.json()['missing_list'])
        self.assertIsNotNone(res_file_validate.json()['summary'])
