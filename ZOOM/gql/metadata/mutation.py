from django import http
import graphene
from graphene_django.rest_framework.mutation import SerializerMutation

from gql.metadata.serializers import FileSourceSerializer


class FileSourceMutation(SerializerMutation):
    class Meta:
        serializer_class = FileSourceSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if 'id' in input:
            instance = FileSourceSerializer.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        return {'data': input, 'partial': True}


class Mutation(graphene.ObjectType):
    file_source = FileSourceMutation.Field()
