from rest_framework import serializers
from indicator import models as indicator_models
from api.generics.serializers import DynamicFieldsModelSerializer

class IndicatorSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = indicator_models.IndicatorDatapoint
        fields = ('id', "measure_value")