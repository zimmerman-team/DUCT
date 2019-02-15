import json

import graphene
import pandas as pd
from django import http
from django.conf import settings
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers

from error_correction.utils import (delete_data, error_correction, get_errors,
                                    update)
from gql.metadata.serializers import (FileErrorCorrectionSerializer,
                                      FileSerializer, FileSourceSerializer,
                                      FileTagsSerializer,
                                      FileValidateSerializer,
                                      SurveyDataSerializer,
                                      FileValidationResultsSerializer)
from lib.tools import check_file_formatting
from metadata.models import File, FileSource, FileTags, SurveyData
from validate.validator import generate_error_data, validate


class FileSourceMutation(SerializerMutation):
    class Meta:
        serializer_class = FileSourceSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if input.get('id', None):
            instance = FileSource.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        # A foreign key bugs on SerializerMutation
        serializer = FileSourceSerializer(data=input)
        if not serializer.is_valid():
            raise Exception(serializer.errors)

        return {'data': input, 'partial': True}

    @classmethod
    def perform_mutate(cls, serializer, info):
        obj = serializer.save()

        kwargs = {}
        for f, field in serializer.fields.items():
            if not isinstance(field, serializers.SerializerMethodField):
                kwargs[f] = field.get_attribute(obj)
            else:
                kwargs[f] = getattr(serializer, field.method_name)(obj)

        return cls(errors=None, **kwargs)


class FileMutation(SerializerMutation):
    class Meta:
        serializer_class = FileSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_file_heading_list(cls, file_name):
        df_file = pd.read_csv(file_name)
        _, dtypes_dict = generate_error_data(df_file)
        return pd.Series(dtypes_dict).to_json()

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if 'id' in input:
            instance = File.objects.filter(
                id=input['id']).first()
            if instance:
                if input['file']:
                    instance.file.name = '{media_root}/{filename}'.format(
                        media_root=settings.MEDIA_ROOT, filename=input['file']
                    )
                    # file input should be file type
                    input['file'] = instance.file

                # Update tags
                if 'tags' in input:
                    # delete all existing tags before update it
                    for tag in instance.tags.all():
                        instance.tags.remove(tag)

                    for item in input['tags']:
                        try:
                            tag = FileTags.objects.get(name=item['name'])
                            instance.tags.add(tag)
                        except FileTags.DoesNotExist:
                            pass

                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        # Temporary instance to save file from a directory
        instance = File()
        instance.file.name = '{media_root}/{filename}'.format(
            media_root=settings.MEDIA_ROOT, filename=input['file']
        )
        input['file'] = instance.file

        # The frontend is needed file_heading_list
        input['file_heading_list'] = \
            cls.get_file_heading_list(instance.file.name)

        # Some bugs on SerializerMutation
        # We need to validate before continue to the next process
        serializer = FileSerializer(data=input)
        if not serializer.is_valid():
            raise Exception(serializer.errors)

        return {'data': input, 'partial': True}

    @classmethod
    def perform_mutate(cls, serializer, info):
        obj = serializer.save()

        kwargs = {}
        for f, field in serializer.fields.items():
            if not isinstance(field, serializers.SerializerMethodField):
                kwargs[f] = field.get_attribute(obj)
            else:
                kwargs[f] = getattr(serializer, field.method_name)(obj)

        return cls(errors=None, **kwargs)


class FileTagsMutation(SerializerMutation):
    class Meta:
        serializer_class = FileTagsSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if input.get('id', None):
            instance = FileTags.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        # A foreign key bugs on SerializerMutation
        serializer = FileTagsSerializer(data=input)
        if not serializer.is_valid():
            raise Exception(serializer.errors)

        return {'data': input, 'partial': True}


class SurveyDataMutation(SerializerMutation):
    class Meta:
        serializer_class = SurveyDataSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if input.get('id', None):
            instance = SurveyData.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        # A foreign key bugs on SerializerMutation
        serializer = SurveyDataSerializer(data=input)
        if not serializer.is_valid():
            raise Exception(serializer.errors)

        return {'data': input, 'partial': True}


class FileValidateMutation(SerializerMutation):
    class Meta:
        serializer_class = FileValidateSerializer

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if input.get('id', None):
            instance = File.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        raise Exception(({'id': "required"}))

    @classmethod
    def perform_mutate(cls, serializer, info):
        file = serializer.instance
        result = check_file_formatting(file.file)

        kwargs = {}
        for f, field in serializer.fields.items():
            if f not in ['success', 'error']:
                kwargs[f] = field.get_attribute(file)

        if result[0]:
            kwargs['success'] = True
        else:
            kwargs['success'] = False
            kwargs['error'] = result[1]['error']

        return cls(errors=None, **kwargs)


class FileErrorCorrectionMutation(SerializerMutation):
    class Meta:
        serializer_class = FileErrorCorrectionSerializer

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if input.get('id', None):
            instance = File.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        raise Exception(({'id': "required"}))

    @classmethod
    def perform_mutate(cls, serializer, info):
        file = serializer.instance
        data = json.loads(serializer.validated_data['command'])
        context = None

        if data['update']:
            try:
                context = update(data['file_id'], data['update_data'])
            except Exception as e:
                context['error'] = "Error occurred when updating file"
                context['success'] = 0
                raise Exception(context)
        elif data['delete']:
            try:
                context = delete_data(
                    data['file_id'],
                    data['delete_data'])
            except Exception as e:
                context[
                    'error'] = "Error occurred when deleting data from file"
                context['success'] = 0
                raise Exception(context)
        elif data['error_toggle']:
            try:
                context = get_errors(data)
                data['error_data'] = context
            except Exception as e:
                context['error'] = "Error occurred when retrieving errors"
                context['success'] = 0
                raise Exception(context)

        context = error_correction(data)

        kwargs = {}
        for f, field in serializer.fields.items():
            if f not in ['command', 'result']:
                kwargs[f] = field.get_attribute(file)

        kwargs['command'] = serializer.validated_data['command']
        kwargs['result'] = pd.Series(context).to_json()

        return cls(errors=None, **kwargs)


class FileValidationResultsMutation(SerializerMutation):
    class Meta:
        serializer_class = FileValidationResultsSerializer

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if input.get('id', None):
            instance = File.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        raise Exception(({'id': "required"}))

    @classmethod
    def perform_mutate(cls, serializer, info):
        file = serializer.instance
        results = validate(file.id)

        kwargs = {}
        for f, field in serializer.fields.items():
            if f not in ['found_list', 'missing_list', 'summary']:
                kwargs[f] = field.get_attribute(file)

        if results:
            kwargs['found_list'] = pd.Series(
                [a for a in results['found_list']]).to_json()
            kwargs['missing_list'] = pd.Series(
                [a for a in results['missing_list']]).to_json()
            kwargs['summary'] = pd.Series(
                [a for a in results['summary']]).to_json()

        return cls(errors=None, **kwargs)


class Mutation(graphene.ObjectType):
    file_source = FileSourceMutation.Field()
    file = FileMutation.Field()
    file_tags = FileTagsMutation.Field()
    survey_data = SurveyDataMutation.Field()
    file_validate = FileValidateMutation.Field()
    file_error_correction = FileErrorCorrectionMutation.Field()
    file_validation_results = FileValidationResultsMutation.Field()
