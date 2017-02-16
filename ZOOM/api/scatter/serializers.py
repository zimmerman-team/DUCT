from rest_framework import serializers
from indicator import models as indicator_models
from api.generics.serializers import DynamicFieldsModelSerializer


class ScatterSerializer(DynamicFieldsModelSerializer):

        class Meta:
                model = indicator_models.ScatterData
                fields = (
                'id',
                'Category',
                'Indicator_1',
                'Indicator_1_value',
                'Indicator_2',
                'Indicator_2_value',
                'Country',
                )