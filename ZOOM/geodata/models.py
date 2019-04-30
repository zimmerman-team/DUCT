from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from django.db import models

GEOTYPE_HEADINGS = [
    'country',
    'region',
    'subnational',
    'city',
    'pointbased',
    'iso3',
    'iso2',
    'province',
    'postcode'
]
SAVED_TYPES = [
    'country', 'region', 'subnational', 'city', 'province', 'postcode'
]
COUNTRY_RELATION_TYPES = [
    'subnational', 'city', 'province', 'postcode'
]


class Geolocation(models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    tag = models.CharField(unique=True, max_length=200)
    iso2 = models.CharField(unique=True, max_length=2, null=True)
    iso3 = models.CharField(unique=True, max_length=3, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    type = models.CharField(
        max_length=100,
        choices=(
            ('country', 'country'),
            ('region', 'region'),
            ('subnational', 'subnational'),
            ('city', 'city'),
            ('pointbased', 'pointbased'),
            ('province', 'province'),
            ('postcode', 'postcode'),
        )
    )
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)

    def __str__(self):
        return self.tag


class Region(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    name = gis_models.CharField(max_length=200)
    code = gis_models.CharField(max_length=100, null=True)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    language = gis_models.CharField(max_length=2, null=True)
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    def __unicode__(self):
        return self.name


class Country(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    name = gis_models.CharField(unique=True, max_length=100, db_index=True)
    primary_name = gis_models.BooleanField(default=False)
    iso2 = gis_models.CharField(unique=True, max_length=2, null=True)
    iso3 = gis_models.CharField(unique=True, max_length=3, null=True)
    numerical_code_un = gis_models.IntegerField(null=True, blank=True)
    dac_country_code = gis_models.IntegerField(null=True, blank=True)
    capital_city = gis_models.OneToOneField(
        "City",
        related_name='capital_of',
        null=True,
        blank=True,
        on_delete=gis_models.SET_NULL)
    region = gis_models.ForeignKey(
        Region,
        null=True,
        blank=True,
        on_delete=gis_models.SET_NULL)
    un_region = gis_models.ForeignKey(
        'Region',
        null=True,
        blank=True,
        related_name='un_countries',
        on_delete=gis_models.SET_NULL)
    unesco_region = gis_models.ForeignKey(
        'Region',
        null=True,
        blank=True,
        related_name='unesco_countries',
        on_delete=gis_models.SET_NULL)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    language = gis_models.CharField(max_length=2, null=True)
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    class Meta:
        verbose_name_plural = "countries"

    def __unicode__(self):
        return self.name


class City(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    name = gis_models.CharField(unique=True, max_length=200)
    ascii_name = gis_models.CharField(max_length=200, null=True, blank=True)
    country = gis_models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=gis_models.SET_NULL)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    language = gis_models.CharField(max_length=2, null=True)
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    @property
    def is_capital(self):
        return hasattr(self, 'capital_of')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


class SubNational(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    name = gis_models.CharField(unique=True, max_length=100)
    iso_3166_2 = gis_models.CharField(null=True, blank=True, max_length=2)
    code_local = gis_models.CharField(null=True, blank=True, max_length=100)
    postcode = gis_models.CharField(null=True, blank=True, max_length=100)
    country = gis_models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=gis_models.SET_NULL)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    language = gis_models.CharField(max_length=2, null=True)
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "admin1 regions"


class PointBased(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    name = gis_models.CharField(max_length=200)
    type = gis_models.CharField(max_length=200, null=True, blank=True)
    subnational = gis_models.ForeignKey(
        SubNational, null=True, blank=True, on_delete=gis_models.SET_NULL)
    center_longlat = gis_models.PointField(null=True, blank=True)
    comment = gis_models.TextField()
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    @property
    def is_capital(self):
        return hasattr(self, 'capital_of')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


class Province(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    name = gis_models.CharField(max_length=200)
    ascii_name = gis_models.CharField(max_length=200, null=True, blank=True)
    country = gis_models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=gis_models.SET_NULL)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    language = gis_models.CharField(max_length=2, null=True)
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    class Meta:
        unique_together = ("country", "name")

    def __unicode__(self):
        return self.name


class PostCode(gis_models.Model):
    id = gis_models.AutoField(primary_key=True, editable=False)
    code = gis_models.CharField(max_length=200)
    country = gis_models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=gis_models.SET_NULL)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygons = gis_models.GeometryField(null=True, blank=True)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    language = gis_models.CharField(max_length=2, null=True)
    data_source = gis_models.CharField(max_length=100, null=True, blank=True)
    objects = gis_models.Manager()

    class Meta:
        unique_together = ("country", "code")

    def __unicode__(self):
        return self.code
