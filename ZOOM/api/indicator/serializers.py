from rest_framework import serializers
from indicator import models as indicator_models
from geodata import models as geo_models
from file_upload.models import File, FileTag, FileSource
from api.generics.serializers import DynamicFieldsModelSerializer


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = geo_models.Region
        fields = (
            'code',
            'name',
        )


class CountrySerializer(serializers.ModelSerializer):

    region = RegionSerializer()
    
    class Meta:
        model = geo_models.Country
        fields = (
            'code',
            'name',
            'region',
        )

class FileSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model=FileSource
        fields = (
            'name',
        )

class FileTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FileTag
        fields = (
            'name',
        )


class FileSerializer(serializers.ModelSerializer):
    file_tags = FileTagSerializer(source="tags", many=True, read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'file_name',
            'created',
            'file_tags',
            'status',
            'authorised',
        )

    #data_source = FileSourceSerializer()

#getting error when adding data source to file serializer, think it's due to nested serializers therefore using this cutsom serializer instead
class FileDataSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        file_name = value.file_name
        data_source = value.data_source.name
        title = value.title
        created = value.created
        description = value.description
        authorised = value.authorised
        tags = value.tags.all()
        tag_list = []
        for i in tags:
            tag_list.append(i.name)
        file_dict = {"file_name" : file_name, "file_source" : data_source, "file_title" : title, "description" : description, "authorised" : authorised, "tags" : tag_list}
        return file_dict

class IndicatorSubCatSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        file_name = value.file_name
        data_source = value.data_source.name
        title = value.title
        created = value.created
        description = value.description
        tags = value.tags.all()
        tag_list = []
        for i in tags:
            tag_list.append(i.name)
        file_dict = {"file_name" : file_name, "file_source" : data_source, "file_title" : title, "description" : description, "tags" : tag_list}
        return file_dict


class IndicatorFilterHeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = indicator_models.IndicatorFilterHeading
        fields = (
            'name'
        )


class IndicatorDataSerializer(serializers.ModelSerializer):

    country = CountrySerializer()
    #file = FileSerializer()
    file = FileDataSerializer()
    #indicator_category = IndicatorCategorySerializer()

    class Meta:
        model = indicator_models.IndicatorDatapoint
        fields = (
            'id',
            'file',
            'date_format',
            #'indicator_category',
            'indicator',
            'country',
            'date_value',
            'source',
            "measure_value",
            "unit_of_measure",
            'other',
            'date_created'
        )


class IndicatorFilterSerializer(serializers.ModelSerializer):

    #return list here


    class Meta:
        model = indicator_models.IndicatorFilter
        heading = IndicatorFilterHeadingSerializer()
        measure_value = IndicatorDataSerializer()
        file_source = FileSourceSerializer()
        
        fields = (
            'name',
            'heading',
            'measure_value',
            'file_source'
        )

class IndicatorSerializer(serializers.ModelSerializer):
    file_source = FileSourceSerializer()
    class Meta:
        model = indicator_models.Indicator
        fields = (
            'id',
            'description',
            'count',
            'file_source'
        )


