from rest_framework import serializers

from metadata.models import File, FileSource


class FileSourceSerializer(serializers.ModelSerializer):
    entry_id = serializers.SerializerMethodField()

    class Meta:
        model = FileSource
        fields = (
            'id',
            'name',
            'entry_id'
        )


class FileSerializer(serializers.ModelSerializer):
    entry_id = serializers.SerializerMethodField()

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
            'entry_id',
            'file_heading_list'
        )
