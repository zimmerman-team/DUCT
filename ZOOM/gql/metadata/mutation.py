from django import http
from django.conf import settings

import graphene
from graphene_django.rest_framework.mutation import SerializerMutation

from metadata.models import FileSource, File
from gql.metadata.serializers import FileSourceSerializer, FileSerializer


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


class FileMutation(SerializerMutation):
    class Meta:
        serializer_class = FileSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

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

        # Some bugs on SerializerMutation
        # We need to validate before continue to the next process
        serializer = FileSerializer(data=input)
        if not serializer.is_valid():
            raise Exception(serializer.errors)

        return {'data': input, 'partial': True}


class Mutation(graphene.ObjectType):
    file_source = FileSourceMutation.Field()
    file = FileMutation.Field()
