from rest_framework import serializers

from file_upload.models import File, FileTag, FileSource


class FileTagSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = FileTag
		fields = (
			'id',
			'name')


class FileSourceSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = FileSource
		fields = (
			# 'id',
			'name',
			)


class FileSerializer(serializers.ModelSerializer):
	file = serializers.FileField()
	tags = FileTagSerializer(many=True, read_only=True)
	data_source = FileSourceSerializer(read_only=True)

	class Meta:
		model = File
		fields = (
			'id',
			'title',
			'description',
			'file',
			'file_name',
			'in_progress',
			'source_url',
			'data_source',
			'tags',
			'created',
			'modified',
			'rendered')

