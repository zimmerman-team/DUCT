from rest_framework import serializers
from rest_framework.fields import SkipField

from collections import OrderedDict


class DynamicFieldsSerializer(serializers.Serializer):
    """
    Serializer allowing for dynamic field instantiation
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', ())

        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)

        if len(fields) > 0:
            allowed = set(fields)
            existing = set(self.fields.keys())

            if 'all' in allowed:
                return

            for field_name in existing - allowed:
                self.fields.pop(field_name)

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer allowing for dynamic field instantiation
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', ())

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if len(fields) > 0:
            allowed = set(fields)
            existing = set(self.fields.keys())

            if 'all' in allowed:
                return

            for field_name in existing - allowed:
                self.fields.pop(field_name)

