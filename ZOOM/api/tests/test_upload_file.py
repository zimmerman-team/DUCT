import os

from django.conf import settings
from django.test import TestCase
from django.test import Client


class UploadFileTestCase(TestCase):
    """
    To test this guy UNIT_TEST in the settings configuration should be True.
    So please put it in the local_settings.py
    """

    def test_file_upload(self):
        settings.UNIT_TEST = True
        client = Client()
        with open(os.path.abspath("samples/AIDSinfotest.csv")) as fp:
            response = client.post('/api/metadata/upload/', {'file': [fp]})

        self.assertIsNotNone(response.data.get('url'))
