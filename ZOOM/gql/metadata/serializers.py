import json

import pandas as pd
from rest_framework import serializers

from indicator.models import MAPPING_DICT
from metadata.models import File, FileSource, FileTags


class FileSourceSerializer(serializers.ModelSerializer):
    entry_id = serializers.SerializerMethodField()

    class Meta:
        model = FileSource
        fields = (
            'id',
            'name',
            'entry_id'
        )

    @classmethod
    def get_entry_id(cls, obj):
        return str(obj.id)


class FileTagsSerializer(serializers.ModelSerializer):
    entry_id = serializers.SerializerMethodField()

    class Meta:
        model = FileTags
        fields = (
            'id',
            'name',
            'entry_id'
        )

    @classmethod
    def get_entry_id(cls, obj):
        return str(obj.id)


class FileSerializer(serializers.ModelSerializer):
    entry_id = serializers.SerializerMethodField()
    entry_file_heading_list = serializers.SerializerMethodField()
    data_model_heading = serializers.SerializerMethodField()
    tags = FileTagsSerializer(many=True, read_only=True, required=False)

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
            'file_heading_list',
            'entry_id',
            'entry_file_heading_list',
            'data_model_heading',
            'tags'
        )

    @classmethod
    def get_entry_id(cls, obj):
        return str(obj.id)

    @classmethod
    def get_entry_file_heading_list(cls, obj):
        return json.loads(obj.file_heading_list)

    @classmethod
    def get_data_model_heading(cls, obj):
        return json.loads(pd.Series(MAPPING_DICT).to_json())




