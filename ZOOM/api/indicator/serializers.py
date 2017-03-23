from rest_framework import serializers
from indicator import models as indicator_models
from geodata import models as geo_models
from api.generics.serializers import DynamicFieldsModelSerializer



class IndicatorCategoryIdSerializer(DynamicFieldsModelSerializer):

	class Meta:
		model = indicator_models.IndicatorCategory
		fields = (
        	'id',
        	'code'
        	)		


class RegionIdSerializer(DynamicFieldsModelSerializer):

        class Meta:
                model = geo_models.Region
                fields = (
                'code',
                'name',
                )

class CountryIdSerializer(DynamicFieldsModelSerializer):

        region = RegionIdSerializer()
        class Meta:
                model = geo_models.Country
                fields = (
                'code',
                'name',
                'region',
                )


class IndicatorSerializer(DynamicFieldsModelSerializer):

	country_id = CountryIdSerializer()
        
	# indicator_category_id = IndicatorCategoryIdSerializer()
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
