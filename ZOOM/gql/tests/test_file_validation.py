import os

from django.test import TestCase
from geodata.importer.country import CountryImport
from gql.tests import factory

from validate.validator import validate


class FileValdationTestCase(TestCase):

    def setUp(self):
        ci = CountryImport()
        ci.update_polygon()
        ci.update_alt_name()

        self.dummy_file_source = factory.FileSourceFactory(
            name='dummy_file_source'
        )
        self.dummy_geolocation = factory.GeolocationFactory(
            tag='Albania',
            iso2='al',
            iso3='alb',
            object_id=4,
            content_type_id=15,
            type='country'
        )
        self.dummy_file = factory.FileFactory(
            title="test",
            description="test",
            contains_subnational_data=True,
            organisation="test",
            maintainer="test",
            date_of_dataset="2009-01-01",
            methodology="test",
            define_methodology="test",
            update_frequency="test",
            comments="test",
            accessibility="p",
            data_quality="test",
            number_of_rows=1,
            file_types="csv",
            location=self.dummy_geolocation,
            source=self.dummy_file_source,
            file=os.path.abspath("samples/AIDSinfotest.csv")
        )

    def test_validate(self):
        response = validate(self.dummy_file.id)
        self.assertIsNotNone(response)
