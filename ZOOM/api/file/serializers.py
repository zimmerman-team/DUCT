from rest_framework import serializers

from metadata.models import File, FileSource

class FileSourceSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = FileSource
		fields = (
			'name',
			)

class FileSerializer(serializers.ModelSerializer):
	file = serializers.FileField()
	data_source = FileSourceSerializer(read_only=True)

	class Meta:
		model = File
		fields = (
			'file_id',
			'description',
	)

