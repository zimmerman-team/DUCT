from rest_framework import serializers
from indicator import models as indicator_models
from geodata import models as geo_models
from api.generics.serializers import DynamicFieldsModelSerializer



class IndicatorCategoryIdSerializer(serializers.ModelSerializer):

	class Meta:
		model = indicator_models.IndicatorCategory
		fields = (
        	'id',
        	'code'
        	)		


class RegionIdSerializer(serializers.ModelSerializer):

        class Meta:
                model = geo_models.Region
                fields = (
                'code',
                'name',
                )

class CountryIdSerializer(serializers.ModelSerializer):

        region = RegionIdSerializer()
        class Meta:
                model = geo_models.Country
                fields = (
                'code',
                'name',
                'region',
                )

class FileTagsSerializer(serializers.ModelSerializer):
        class Meta:
                model = indicator_models.FileTags
                fields = (
                        'file_id',
                        'tag',
                        )

class FileSourceSerializer(serializers.ModelSerializer):
        file_tags = FileTagsSerializer(many=True, read_only=True)
        class Meta:
                model = indicator_models.FileSource
                fields = (
                        'id',
                        'file_name',
                        'date_uploaded',
                        'file_tags',
                        )

class IndicatorCategoryIdSerializer(serializers.ModelSerializer):
        class Meta:
                model = indicator_models.IndicatorCategory
                fields = (
                        'id',
                        'code',
                        'indicator',
                        )     

class IndicatorSerializer(serializers.ModelSerializer):

	country_id = CountryIdSerializer()
        file_source_id = FileSourceSerializer()
        # indicator_category_id = IndicatorCategoryIdSerializer(many=True, read_only=True)
        
	indicator_category_id = IndicatorCategoryIdSerializer()

	class Meta:
		model = indicator_models.IndicatorDatapoint
		fields = (
        	'id',
        	'file_source_id',
        	'date_format_id',
        	'indicator_category_id',
        	'indicator_id',
        	'country_id',
        	'date_value',
        	'source_id',
        	"measure_value",
        	'other',
        	)
