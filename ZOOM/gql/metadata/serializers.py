import json

import pandas as pd
from rest_framework import serializers, fields

from indicator.models import MAPPING_DICT
from metadata.models import (
    File, FileSource, FileTags, SurveyData,
    WHO_TESTED_CHOICES,
    CLEANING_TECHNIQUES_CHOICES
)


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
            'tags',
            'survey_data'
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


class SurveyDataSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    entry_id = serializers.SerializerMethodField()
    who_did_you_test_with = fields.MultipleChoiceField(
        choices=WHO_TESTED_CHOICES
    )
    data_cleaning_techniques = fields.MultipleChoiceField(
        choices=CLEANING_TECHNIQUES_CHOICES
    )

    class Meta:
        model = SurveyData
        fields = (
            'id',
            'entry_id',
            'have_you_tested_tool',
            'who_did_you_test_with',
            'considered_senstive',
            'staff_trained',
            'ask_sensitive',
            'select_respondents',
            'how_many_respondents',
            'edit_sheet',
            'data_cleaning_techniques',
            'other_cleaning_technique'
        )

    @classmethod
    def get_id(cls, obj):
        return str(obj.id)

    @classmethod
    def get_entry_id(cls, obj):
        return str(obj.id)


class FileValidateSerializer(serializers.ModelSerializer):
    success = serializers.BooleanField(read_only=True)
    error = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'success',
            'error'
        )


class FileErrorCorrectionSerializer(serializers.ModelSerializer):
    command = serializers.JSONField()
    result = serializers.JSONField(read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'command',
            'result'
        )


class FileValidationResultsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    entry_id = serializers.SerializerMethodField()
    found_list = serializers.JSONField(read_only=True)
    missing_list = serializers.JSONField(read_only=True)
    summary = serializers.JSONField(read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'entry_id',
            'found_list',
            'missing_list',
            'summary'
        )


class FileDeleteSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    message = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'message'
        )
