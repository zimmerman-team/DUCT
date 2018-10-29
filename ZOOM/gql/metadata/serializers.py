from rest_framework import serializers

from geodata.models import Geolocation
from metadata.models import File, FileSource


class FileSourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileSource
        fields = (
            'id',
            'name',
        )


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = (
            'id',
            'title',
            'description',
            'contains_subnational_data',
            'organisation',
            'maintainer',
            'date_of_dataset',
            'methodology',
            'define_methodology',
            'update_frequency',
            'comments',
            'accessibility',
            'data_quality',
            'number_of_rows',
            'number_of_rows_saved',
            'file_types',
            'data_uploaded',
            'last_updated',
            'location',
            'source',
            'file',
        )
