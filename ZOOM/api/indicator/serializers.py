from rest_framework import serializers
from indicator import models as indicator_models
from geodata import models as geo_models
from file_upload.models import File, FileTag
from api.generics.serializers import DynamicFieldsModelSerializer


class IndicatorCategoryIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = indicator_models.IndicatorCategory
        fields = (
            'id',
            'code')


class RegionIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = geo_models.Region
        fields = (
            'code',
            'name')


class CountryIdSerializer(serializers.ModelSerializer):

    region = RegionIdSerializer()
    
    class Meta:
        model = geo_models.Country
        fields = (
            'code',
            'name',
            'region')


class FileTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FileTag
        fields = (
            'file_id',
            'tag')


class FileSerializer(serializers.ModelSerializer):
    file_tags = FileTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = File
        fields = (
            'id',
            'file_name',
            'date_uploaded',
            'file_tags')


class IndicatorCategoryIdSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = indicator_models.IndicatorCategory
        fields = (
            'id',
            'code',
            'indicator') 


class IndicatorSerializer(serializers.ModelSerializer):

    country_id = CountryIdSerializer()
    file = FileSerializer()
    indicator_category_id = IndicatorCategoryIdSerializer()


    class Meta:
        model = indicator_models.IndicatorDatapoint
        fields = (
            'id',
            'file',
            'date_format_id',
            'indicator_category_id',
            'indicator_id',
            'country_id',
            'date_value',
            'source_id',
            "measure_value",
            "unit_of_measure",
            'other')
