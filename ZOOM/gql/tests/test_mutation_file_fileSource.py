from gql.schema import schema
from django.test import TestCase
from metadata.models import FileSource, File
from gql.tests import factory
import os


class MutationTestCase(TestCase):
    def setUp(self):
        # Dummy objects
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
            file: "datasets/AIDSinfotest.csv"

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

        schema.execute(query)

        self.assertTrue(File.objects.filter(title='test')
                        .filter(description='test')
                        .filter(contains_subnational_data=True)
                        .filter(organisation='test')
                        .filter(maintainer='test')
                        .filter(date_of_dataset="2009-01-01")
                        .filter(methodology="test")
                        .filter(define_methodology="test")
                        .filter(update_frequency="test")
                        .filter(comments="test")
                        .filter(accessibility="p")
                        .filter(data_quality="test")
                        .filter(number_of_rows=1)
                        .filter(file_types="csv")
                        .filter(location=location)
                        .filter(source=source)
                        .filter(file=os.path.abspath
                                ("media/datasets/AIDSinfotest.csv")).
                        exists())
