from django import http
import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers

from mapping.models import Mapping
from metadata.models import File
from gql.mapping.serializers import MappingSerializer
from gql.utils import get_session_email


class MappingMutation(SerializerMutation):

    class Meta:
        serializer_class = MappingSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        file_id = input['data']['metadata_id']
        input['error_message'] = ''
        input['status'] = 'INITIAL'
        input['task_id'] = ''
        input['session_email'] = get_session_email()

        try:
            file = File.objects.get(id=file_id)
            input['file'] = file.id

            try:
                mapping = Mapping.objects.get(file=file)
                input['id'] = mapping.id
            except Mapping.DoesNotExist:
                pass

        except File.DoesNotExist:
            raise Exception(
                'file with metadata_id={file_id} not found!'.format(
                    file_id=file_id
                )
            )

        if 'id' in input:
            instance = Mapping.objects.filter(id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        serializer = MappingSerializer(data=input)
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


class Mutation(graphene.ObjectType):
    mapping = MappingMutation.Field()
