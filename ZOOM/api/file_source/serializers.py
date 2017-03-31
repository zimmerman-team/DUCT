from rest_framework import serializers
from indicator.models import FileSource, FileTags





class FileSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model = FileSource
		fields = (
			'id',
			'file_name',
			'date_uploaded',
			)

class FileTagsSerializer(serializers.ModelSerializer):
	class Meta:
		model = FileTags
		fields = (
			'id',
			'tag',
			)