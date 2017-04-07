from rest_framework import serializers
from validate.models import File
from indicator.models import FileSource


class FileSerializer(serializers.ModelSerializer):

	file = serializers.FileField()

	class Meta:
		model = File
		read_only_fields = (
        	'file',
        	)		

class MapperSerializer(serializers.ModelSerializer):
	file_name = serializers.CharField() 
	class Meta:
		model = FileSource
		fields = (
            'file_name',
            # 'date_uploaded',
            )
