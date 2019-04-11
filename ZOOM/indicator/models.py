from django.db import models

from geodata.models import Geolocation, Country
from metadata.models import File, FileSource

MAPPING_HEADINGS = {  # Main mapping information
    'indicator': [],
    'filters': [],
    'geolocation': [],
    'date': [],
    'value_format': [],
    'value': [],
    'comment': [],
}
# Heading to give each column selected as a filter, dictionary format ->
# {file column heading: desired heading value}
FILTER_HEADINGS = 'filter_headings'

EXTRA_INFORMATION = {
    'empty_entries':  # Values that are compulsory, if mapping is not provided
    # then user must enter value for empty mapping
    {
        'empty_indicator': '',
        # Value of chosen geolocation. Typpe of geolocation choosen Regional,
        # Subnational or Country
        'empty_geolocation': {'value': '', 'type': ''},
        'empty_filter': '',
        # File column heading: associated data type (Numeric percentage
        # etc)
        'empty_value_format': {},
        'empty_date': '',
        'empty_value': '',
    },
    'multi_mapped':
        {
            # Columns headings that are associated with datamodel, dictionary
            # format
            'column_heading': {},
            # The values within the column that are associated with datamodel,
            # dictionary format
            'column_values': {},
    },
    'point_based_info':
        {
            'coord': {'lat': '', 'lon': ''},  # Coordinates of point
            'subnational': '',  # Subnational region point lies in
            'country': '',  # Country point lies in
            'type': '',
            # Type of point based_data. eg. Hospital,
            # School, encounter, attack etc
    }
}

MAPPING_DICT = {
    'metadata_id': '',
    'mapping_dict': MAPPING_HEADINGS,  # Must always have
    FILTER_HEADINGS: {},  # Must always have
    'extra_information': EXTRA_INFORMATION
}


class DateFormat(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    type = models.CharField(unique=True, max_length=200)


class ValueFormat(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    type = models.CharField(unique=True, max_length=200)


class Indicator(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    file_source = models.ForeignKey(FileSource, on_delete=models.CASCADE)
    file = models.OneToOneField(File, on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True
    )


class FilterHeadings(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # Allow aggregation on a column within ZOOM
    aggregation_allowed = models.BooleanField(default=False)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)


class Datapoints(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    value = models.FloatField()
    date = models.CharField(max_length=200)  # Int
    comment = models.TextField(null=True, blank=True)

    value_format = models.ForeignKey(
        ValueFormat, on_delete=models.SET_NULL, null=True)
    date_format = models.ForeignKey(
        DateFormat, on_delete=models.SET_NULL, null=True)

    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    metadata = models.ForeignKey(File, on_delete=models.CASCADE)
    geolocation = models.ForeignKey(Geolocation, on_delete=models.CASCADE)


class Filters(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    heading = models.ForeignKey(FilterHeadings, on_delete=models.CASCADE)
    metadata = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    datapoints = models.ManyToManyField(Datapoints, related_name='filters')
    geolocations = models.ManyToManyField(Geolocation)

    value_format = models.ForeignKey(
        ValueFormat, on_delete=models.SET_NULL, null=True)
    date_format = models.ForeignKey(
        DateFormat, on_delete=models.SET_NULL, null=True)

    # For filtering, makes it quicker#
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)


def clean_up_indicators():
    indicators = Indicator.objects.all()
    for ind in indicators:
        filterInd = Datapoints.objects.filter(indicator=ind)
        if filterInd.count() == 0:
            ind.delete()
