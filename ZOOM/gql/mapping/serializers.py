from rest_framework import serializers

from mapping.models import Mapping


class MappingSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    entry_id = serializers.SerializerMethodField()

    class Meta:
        model = Mapping
        fields = (
            'id',
            'data',
            'entry_id',
            'file',
            'status',
            'error_message',
            'task_id',
            'session_email'
        )

    @classmethod
    def get_id(cls, obj):
        return str(obj.id)

    @classmethod
    def get_entry_id(cls, obj):
        return str(obj.id)
