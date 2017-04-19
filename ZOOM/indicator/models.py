import uuid
import os
import requests
import rfc6266
import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone

from geodata import models as geo_models


CONTENT_TYPE_MAP = {
    'application/json': 'json',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'text/csv': 'csv'
}


def upload_to(instance, filename=''):
	#create datasets if it doesnt exist
    #return os.path.join(str(instance.pk), filename)
    return os.path.join(settings.MEDIA_ROOT + "/datasets/", filename)

#Basic data store for the test file being used


class Indicator(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    description = models.TextField(null=True, blank=True)
    #source = models.ForeignKey(IndicatorSource, null=True, blank=True)
    #category = models.ForeignKey(IndicatorCategory, null=True, blank=True)


class IndicatorCategory(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator,null=False, blank=False)


class IndicatorSource(models.Model):
    id = models.CharField(max_length=500, primary_key=True)
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator,null=False, blank=False)


"""class IndicatorSubgroup(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    #indicator = ForeignKey
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator, null=False, blank=False)"""


class FileSource(models.Model):
    file_name = models.CharField(max_length=100)#set as primary key?
    date_uploaded = models.DateTimeField(default=timezone.now, blank=True, null=True) #for testing purposes


class FileTags(models.Model):
    file_id = models.ForeignKey(FileSource, null=False, blank=False)
    tag =  models.CharField(max_length=50)
    #file_type = models.CharField(max_length = 5)


class Time(models.Model):
    date_type = models.CharField(max_length = 100, primary_key=True)
    #date = models.DateField(("Date")) # mapping time format, timezone?


class Sector(models.Model):#what is this for?
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length = 100)


class Organisation(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length = 100)


class MeasureValue(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length = 100)
    value_type= models.CharField(max_length=50)#might not need
    value = models.DecimalField(max_digits=20, decimal_places = 5)
#other


class IndicatorDatapoint(models.Model):
    file_source_id = models.ForeignKey(FileSource, db_column='file_source_id')
    date_created =  models.DateTimeField(default=timezone.now)
    date_format_id = models.ForeignKey(Time, db_column='date_format_id', blank=True, null=True)
    indicator_id = models.ForeignKey(Indicator, db_column='indicator_id', blank=True, null=True)
    indicator_category_id = models.ForeignKey(IndicatorCategory, db_column='indicator_category_id', blank=True, null=True)
    unit_of_measure = models.CharField(max_length=20, blank=True, null=True)
    country_id = models.ForeignKey(geo_models.Country, db_column='country_id', blank=True, null=True)#should be a foreign key to GeoData
    date_value = models.CharField(max_length=20, blank=True, null=True) #changed from DecimalField #models.DecimalField(max_digits=20, decimal_places = 5) # identify timezone?
    source_id = models.ForeignKey(IndicatorSource, db_column='source_id', blank=True, null=True)
    #changed from foreign key to  Decimal and then to CharField as Pandas.to_sql didn't save properly
    measure_value = models.CharField(max_length=40, blank=True, null=True) #models.DecimalField(max_digits=20, decimal_places = 5)#for now leave as char #models.ForeignKey(MeasureValue) # might need more for accuracy
    other = models.CharField(max_length=600, blank=True, null=True) #found instance where it ius bigger than 500    


#the mapping betweeen coulmns in the datastore and HXL tags
"""class HXLmapping(models.Model): #can be used for other conversions
    indicator =  models.ForeignKey(IndicatorSource, null=True, blank=True)
    models.CharField(max_length = 50)
    HXL_tag = models.ForeignKey(HXLtags) #HXL tags can error tags

#HXL and the corresponding value type for that tag
class HXLtags(models.Model):
    id = models.CharField(max_length = 50, primary_key=True)
    value_type = models.CharField(max_length = 40)"""
