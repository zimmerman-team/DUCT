from rest_framework import serializers
from validate.models import File 



class FileSerializer(serializers.ModelSerializer):

	file = serializers.FileField()

	class Meta:
		model = File
		read_only_fields = (
        	'file',
        	)		
		