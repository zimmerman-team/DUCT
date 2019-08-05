import os

from django.test import TestCase

from gql.schema import schema
from gql.tests import factory
from metadata.models import File, FileSource


class MutationTestCase(TestCase):
    def setUp(self):
        # Dummy objects
        self.dummy_file_source = factory.FileSourceFactory(
            name='dummy_file_source'
        )
        alb = factory.CountryFactory(name='Albania', iso2='al', iso3='alb')
        self.dummy_geolocation = factory.GeolocationFactory(
            tag='Albania',
            iso2='al',
            iso3='alb',
            object_id=alb.id,
            content_type_id=15,
            type='country'
        )

    def test_mutation_file_source(self):
        name = 'something'
        query = """
        mutation fileSource {
            fileSource(input:{name:"%s"}) {
                                    name
            }
        }
        """ % name

        schema.execute(query)

        self.assertTrue(FileSource.objects.filter(name=name).exists())

    def test_mutation_file(self):

        location = self.dummy_geolocation.id
        source = self.dummy_file_source.id
        query_input = """
        input: {
            title: "test",
            description: "test",
            containsSubnationalData: true,
            organisation: "test",
            maintainer: "test",
            dateOfDataset: "2009-01-01",
            methodology: "test",
            defineMethodology: "test",
            updateFrequency: "test",
            comments: "test",
            accessibility: "p",
            dataQuality: "test",
            numberOfRows: 1,
            fileTypes: "csv",
            location: "%s",
            source: "%s",
            file: "AIDSinfotest.csv"

        }""" % (location, source)

        query = """
        mutation file {
            file(%s) {
            id
            description
            containsSubnationalData
            organisation
            maintainer
            dateOfDataset
            methodology
            defineMethodology
            updateFrequency
            comments
            accessibility
            dataQuality
            numberOfRows
            fileTypes
            location
            source
            file
            }
        }""" % query_input

        result = schema.execute(query)
        self.assertEqual(result.errors, None)
