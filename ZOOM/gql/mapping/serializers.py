from rest_framework import serializers

from mapping.models import Mapping


class MappingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mapping
        fields = (
            'id',
            'file',
            'data'
        )
