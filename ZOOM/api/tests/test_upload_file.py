import os

from django.conf import settings
from django.test import TestCase
from django.test import Client


class UploadFileTestCase(TestCase):
    """
    To test this guy UNIT_TEST in the settings configuration should be True.
    So please put it in the local_settings.py
    """

    def setUp(self):
        self.filename = 'AIDSinfotest'

    def test_file_upload(self):
        settings.UNIT_TEST = True
        client = Client()

        ext = '.csv'
        with open(os.path.abspath(
            'samples/{filename}'.format(filename=self.filename + ext))
        ) as fp:
            response = client.post('/api/metadata/upload/', {'file': [fp]})

        self.assertIsNotNone(response.data.get('url'))

    def tearDown(self):
        media_dir = settings.MEDIA_ROOT + '/datasets/'
        for item in os.listdir(media_dir):
            if item.startswith(self.filename):
                os.remove(os.path.join(media_dir, item))
