from rest_framework import serializers

from indicator.models import Indicator


class IndicatorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    entry_id = serializers.SerializerMethodField()

    class Meta:
        model = Indicator
        fields = (
            'id',
            'entry_id',
            'name',
            'description',
            'file_source'
        )

    @classmethod
    def get_id(cls, obj):
        return str(obj.id)

    @classmethod
    def get_entry_id(cls, obj):
        return str(obj.id)
