import json

import pandas as pd
from rest_framework import serializers, fields

from indicator.models import MAPPING_DICT
from metadata.models import (
    File, FileSource, FileTags, SurveyData,
    WHO_TESTED_CHOICES, HOW_SELECT_RESPONDENTS_CHOICES,
    CLEANING_TECHNIQUES_CHOICES
)
from error_correction.utils import DELETE_DICT, UPDATE_DICT


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
    who_did_you_test_with = fields.MultipleChoiceField(
        choices=WHO_TESTED_CHOICES
    )
    select_respondents = fields.MultipleChoiceField(
        choices=HOW_SELECT_RESPONDENTS_CHOICES
    )
    data_cleaning_techniques = fields.MultipleChoiceField(
        choices=CLEANING_TECHNIQUES_CHOICES
    )

    class Meta:
        model = SurveyData
        fields = (
            'id',
            'have_you_tested_tool',
            'who_did_you_test_with',
            'considered_senstive',
            'staff_trained',
            'ask_sensitive',
            'select_respondents',
            'other',
            'how_many_respondents',
            'edit_sheet',
            'data_cleaning_techniques',
        )


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
    data = serializers.JSONField()
    result = serializers.JSONField(read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'data',
            'result'
        )
