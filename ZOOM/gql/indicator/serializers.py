from rest_framework import serializers

from indicator.models import Indicator


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ('id', 'name', 'description', 'file_source')
