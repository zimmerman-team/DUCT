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
from file_upload.models import File, FileSource
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


#Basic data store for the test file being used

class Indicator(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    description = models.TextField(null=True, blank=True)
    count = models.IntegerField(default=0, null=True)
    file_source = models.ForeignKey(FileSource, null=True, blank=True)
    #category = models.ForeignKey(IndicatorCategory, null=True, blank=True)


"""class IndicatorCategory(models.Model):
    unique_identifier = models.CharField(max_length=500, unique=True)
    name = models.CharField(max_length=255, default=None)#adding default to make transition from old to model to new model error free 
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator,null=False, blank=False)
    parent = models.ForeignKey('self', related_name='child', null=True, blank=True)#need child and parent to ensure consistency, ie each entry point to a unique entry
    level = models.IntegerField(default=0)"""

class IndicatorSource(models.Model):
    id = models.CharField(max_length=500, primary_key=True)
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator,null=False, blank=False)

"""class IndicatorSubgroup(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    #indicator = ForeignKey
    code = models.CharField(max_length=50)
    indicator = models.ForeignKey(Indicator, null=False, blank=False)"""


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
    file = models.ForeignKey(File)
    date_created = models.DateTimeField(default=timezone.now)
    date_format = models.ForeignKey(Time, blank=True, null=True)
    indicator = models.ForeignKey(Indicator, blank=True, null=True)
    #indicator_category = models.ForeignKey(IndicatorCategory, blank=True, null=True)
    unit_of_measure = models.CharField(max_length=50, blank=True, null=True)
    country = models.ForeignKey(geo_models.Country, blank=True, null=True)#should be a foreign key to GeoData
    date_value = models.CharField(max_length=20, blank=True, null=True) #changed from DecimalField #models.DecimalField(max_digits=20, decimal_places = 5) # identify timezone?
    source = models.ForeignKey(IndicatorSource, blank=True, null=True)
    #changed from foreign key to  Decimal and then to CharField as Pandas.to_sql didn't save properly
    measure_value = models.CharField(max_length=40, blank=True, null=True) #models.DecimalField(max_digits=20, decimal_places = 5)#for now leave as char #models.ForeignKey(MeasureValue) # might need more for accuracy
    other = models.CharField(max_length=600, blank=True, null=True) #found instance where it ius bigger than 500 
    search_vector_text = SearchVectorField(null=True)
    #filters = models.CharField(blank=True, null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector_text'])
        ]

    def __unicode__(self):
        return unicode(self.id)

#the mapping betweeen coulmns in the datastore and HXL tags
"""class HXLmapping(models.Model): #can be used for other conversions
    indicator =  models.ForeignKey(IndicatorSource, null=True, blank=True)
    models.CharField(max_length = 50)
    HXL_tag = models.ForeignKey(HXLtags) #HXL tags can error tags

#HXL and the corresponding value type for that tag
class HXLtags(models.Model):
    id = models.CharField(max_length = 50, primary_key=True)
    value_type = models.CharField(max_length = 40)"""


class IndicatorFilterHeading(models.Model):
    name = models.CharField(max_length=255, primary_key=True) 
    

class IndicatorFilter(models.Model):
    name = models.CharField(max_length=255)
    heading = models.ForeignKey(IndicatorFilterHeading)
    measure_value = models.ForeignKey(IndicatorDatapoint)
    file_source = models.ForeignKey(FileSource, null=True)
     

def update_indicator_counts():
    indicators = Indicator.objects.all()
    for ind in indicators:
        filterInd = IndicatorDatapoint.objects.filter(indicator=ind)
        if(filterInd.count() != 0):
            ind.file_source = filterInd[0].file.data_source
            ind.count = filterInd.count()
            ind.save()
        else:##has no indicators
            ind.delete()

def clean_up_indicators():
    indicators = Indicator.objects.all()
    for ind in indicators:
        filterInd = IndicatorDatapoint.objects.filter(indicator=ind)
        if filterInd.count() == 0:
            ind.delete()
