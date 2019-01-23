import graphene
import pandas as pd
from django import http
from django.conf import settings
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers

from gql.metadata.serializers import (FileSerializer, FileSourceSerializer,
                                      FileTagsSerializer)
from metadata.models import File, FileSource, FileTags
from validate.validator import generate_error_data


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
            if type(field) != serializers.SerializerMethodField:
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
            if type(field) != serializers.SerializerMethodField:
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


class Mutation(graphene.ObjectType):
    file_source = FileSourceMutation.Field()
    file = FileMutation.Field()
    file_tags = FileTagsMutation.Field()
