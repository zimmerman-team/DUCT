from django.db import models
import uuid
from django.core.urlresolvers import reverse
import os
from django.conf import settings
import requests
from django.core.files.base import ContentFile
import rfc6266  # (content-disposition header parser)
from django.conf import settings
from django.utils import timezone
import datetime

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
    id = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator,null=False, blank=False)
    
class IndicatorSubgroup(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    #indicator = ForeignKey
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator, null=False, blank=False)

class FileSource(models.Model):
    file_name = models.CharField(max_length = 100)
    #file_type = models.CharField(max_length = 5)

class Time(models.Model):
    date_type = models.CharField(max_length = 100, primary_key=True)
    #date = models.DateField(("Date")) # mapping time format, timezone?

class City(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length = 100)

class Country(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length = 100)

class Region(models.Model):
    id = models.CharField(max_length=10, primary_key=True) 
    name = models.CharField(max_length = 100)

class Sector(models.Model):
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
    file_source = models.ForeignKey(FileSource,null= False, blank=False)
    date_created =  models.DateTimeField(default=timezone.now)
    date_format = models.ForeignKey(Time)
    indicator_category = models.ForeignKey(IndicatorCategory)
    indicator = models.ForeignKey(Indicator)
    subgroup = models.ForeignKey(IndicatorSubgroup)
    country = models.ForeignKey(Country)
    date_value = models.DecimalField(max_digits=20, decimal_places = 5) # identify timezone?
    source = models.ForeignKey(IndicatorSource)
    measure_value = models.ForeignKey(MeasureValue) # might need more for accuracy
    other = models.CharField(max_length=200)

#the mapping betweeen coulmns in the datastore and HXL tags
"""class HXLmapping(models.Model): #can be used for other conversions
    indicator =  models.ForeignKey(IndicatorSource, null=True, blank=True)
    models.CharField(max_length = 50)
    HXL_tag = models.ForeignKey(HXLtags) #HXL tags can error tags

#HXL and the corresponding value type for that tag
class HXLtags(models.Model):
    id = models.CharField(max_length = 50, primary_key=True)
    value_type = models.CharField(max_length = 40)"""

