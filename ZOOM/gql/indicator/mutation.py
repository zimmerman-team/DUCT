from django import http
import graphene
from graphene_django.rest_framework.mutation import SerializerMutation

from indicator.models import Indicator
from gql.indicator.serializers import IndicatorSerializer


class IndicatorMutation(SerializerMutation):

    class Meta:
        serializer_class = IndicatorSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if 'id' in input:
            instance = Indicator.objects.filter(
                id=input['id']).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise http.Http404

        # Bugs on SerializerMutation in the foreign key
        # We need to check if get a correct foreign key
        serializer = IndicatorSerializer(data=input)
        if not serializer.is_valid():
            raise Exception(serializer.errors)

        return {'data': input, 'partial': True}


class Mutation(graphene.ObjectType):
    indicator = IndicatorMutation.Field()
