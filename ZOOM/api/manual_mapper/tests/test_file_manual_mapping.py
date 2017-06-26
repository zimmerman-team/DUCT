from django.test import TestCase
from unittest import skip
from django.test import RequestFactory, Client
from rest_framework.test import APIClient


class FileManualMappingTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_file_manual_mapping(self):

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
        Test 3: File Manual Mapping
        '''
        print res.json()['id']
        manual_mapping_data = {
            "file_id": res.json()['id'],
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
            },
            "dtypes_dict": {
                "Indicator": [
                    [
                        "str",
                        "100%"
                    ]
                ],
                "Area": [
                    [
                        "country_name",
                        "62%"
                    ],
                    [
                        "str",
                        "38%"
                    ],
                    [
                        "iso3",
                        "0%"
                    ]
                ],
                "Source": [
                    [
                        "str",
                        "100%"
                    ]
                ],
                "Area ID": [
                    [
                        "iso3",
                        "64%"
                    ],
                    [
                        "str",
                        "36%"
                    ]
                ],
                "Data Value": [
                    [
                        "numeric",
                        "100%"
                    ],
                    [
                        "str",
                        "0%"
                    ]
                ],
                "Footnotes": [
                    [
                        "str",
                        "98%"
                    ],
                    [
                        "str",
                        "2%"
                    ]
                ],
                "Time Period": [
                    [
                        "date",
                        "100%"
                    ]
                ],
                "Unit": [
                    [
                        "str",
                        "100%"
                    ]
                ],
                "Subgroup": [
                    [
                        "str",
                        "100%"
                    ]
                ]
            }
        }
        # print manual_mapping_data

        res_file_manual_mapping = self.c.post(
            '/api/manual-mapper/?format=json', 
            {
            "file_id": res.json()['id'],
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
            },
            "dtypes_dict": {
                "Indicator": [
                    [
                        "str",
                        "100%"
                    ]
                ],
                "Area": [
                    [
                        "country_name",
                        "62%"
                    ],
                    [
                        "str",
                        "38%"
                    ],
                    [
                        "iso3",
                        "0%"
                    ]
                ],
                "Source": [
                    [
                        "str",
                        "100%"
                    ]
                ],
                "Area ID": [
                    [
                        "iso3",
                        "64%"
                    ],
                    [
                        "str",
                        "36%"
                    ]
                ],
                "Data Value": [
                    [
                        "numeric",
                        "100%"
                    ],
                    [
                        "str",
                        "0%"
                    ]
                ],
                "Footnotes": [
                    [
                        "str",
                        "98%"
                    ],
                    [
                        "str",
                        "2%"
                    ]
                ],
                "Time Period": [
                    [
                        "date",
                        "100%"
                    ]
                ],
                "Unit": [
                    [
                        "str",
                        "100%"
                    ]
                ],
                "Subgroup": [
                    [
                        "str",
                        "100%"
                    ]
                ]
            }
            },
            format='json'
            )
        
        # print res_file_manual_mapping

        self.assertEquals(res_file_manual_mapping.status_code, 200, res_file_manual_mapping.json())
        self.assertEquals(res_file_manual_mapping.json()['success'], 1)




