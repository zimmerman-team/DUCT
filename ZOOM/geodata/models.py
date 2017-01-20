from django.contrib.gis.db import models as gis_models
from django.db import models
# from iati_vocabulary.models import RegionVocabulary


# class GeographicVocabulary(models.Model):
#     code = models.CharField(primary_key=True, max_length=20)
#     name = models.CharField(max_length=255)
#     description = models.TextField(default="")
#     url = models.URLField()

#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)

# class PolicyMarkerVocabulary(models.Model):
#     code = models.CharField(max_length=10,  primary_key=True)
#     name = models.CharField(max_length=200)
#     description = models.TextField(default="")

#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)

# class SectorVocabulary(models.Model):
#     code = models.CharField(max_length=10,  primary_key=True)
#     name = models.CharField(max_length=100)
#     description = models.TextField(default="")
#     url = models.URLField()

#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)


# class BudgetIdentifierVocabulary(models.Model):
#     code = models.CharField(primary_key=True, max_length=40)
#     name = models.CharField(max_length=100)
#     description = models.TextField(default="")

#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)

class RegionVocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=100)
    description = models.TextField(default="")

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)

# class HumanitarianScopeVocabulary(models.Model):
#     code = models.CharField(primary_key=True, max_length=40)
#     name = models.CharField(max_length=100)
#     description = models.TextField(default="")

#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)

# class IndicatorVocabulary(models.Model):
#     code = models.CharField(primary_key=True, max_length=2)
#     name = models.CharField(max_length=100)
#     description = models.TextField(default="")
#     url = models.URLField()

#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)

#GeoAppmodels






class Region(gis_models.Model):
    code = gis_models.CharField(primary_key=True, max_length=100)
    name = gis_models.CharField(max_length=80)
    region_vocabulary = gis_models.ForeignKey(RegionVocabulary, default=1)
    parental_region = gis_models.ForeignKey('self', null=True, blank=True)
    center_longlat = gis_models.PointField(null=True, blank=True)
    objects = gis_models.GeoManager()

    def __unicode__(self):
        return self.name


class Country(gis_models.Model):
    code = gis_models.CharField(primary_key=True, max_length=2)
    numerical_code_un = gis_models.IntegerField(null=True, blank=True)
    name = gis_models.CharField(max_length=100, db_index=True)
    alt_name = gis_models.CharField(max_length=100, null=True, blank=True)
    language = gis_models.CharField(max_length=2, null=True)
    capital_city = gis_models.OneToOneField("City", related_name='capital_of', null=True, blank=True)
    region = gis_models.ForeignKey(Region, null=True, blank=True)
    un_region = gis_models.ForeignKey('Region', null=True, blank=True, related_name='un_countries')
    unesco_region = gis_models.ForeignKey('Region', null=True, blank=True, related_name='unesco_countries')
    dac_country_code = gis_models.IntegerField(null=True, blank=True)
    iso3 = gis_models.CharField(max_length=3, null=True, blank=True)
    alpha3 = gis_models.CharField(max_length=3, null=True, blank=True)
    fips10 = gis_models.CharField(max_length=2, null=True, blank=True)
    center_longlat = gis_models.PointField(null=True, blank=True)
    polygon = gis_models.TextField(null=True, blank=True)
    data_source = gis_models.CharField(max_length=20, null=True, blank=True)
    objects = gis_models.GeoManager()

    class Meta:
        verbose_name_plural = "countries"

    def __unicode__(self):
        return self.name


class City(gis_models.Model):
    geoname_id = gis_models.IntegerField(null=True, blank=True)
    name = gis_models.CharField(max_length=200)
    country = gis_models.ForeignKey(Country, null=True, blank=True)
    location = gis_models.PointField(null=True, blank=True)
    ascii_name = gis_models.CharField(max_length=200, null=True, blank=True)
    alt_name = gis_models.CharField(max_length=200, null=True, blank=True)
    namepar = gis_models.CharField(max_length=200, null=True, blank=True)
    objects = gis_models.GeoManager()

    @property
    def is_capital(self):
        return hasattr(self, 'capital_of')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


class Adm1Region(gis_models.Model):
    adm1_code = gis_models.CharField(primary_key=True, max_length=10)
    OBJECTID_1 = gis_models.IntegerField(null=True, blank=True)
    diss_me = gis_models.IntegerField(null=True, blank=True)
    adm1_cod_1 = gis_models.CharField(null=True, blank=True, max_length=20)
    iso_3166_2 = gis_models.CharField(null=True, blank=True, max_length=2)
    wikipedia = gis_models.CharField(null=True, blank=True, max_length=150)
    country = gis_models.ForeignKey(Country, null=True, blank=True)
    adm0_sr = gis_models.IntegerField(null=True, blank=True)
    name = gis_models.CharField(null=True, blank=True, max_length=100)
    name_alt = gis_models.CharField(null=True, blank=True, max_length=200)
    name_local = gis_models.CharField(null=True, blank=True, max_length=100)
    type = gis_models.CharField(null=True, blank=True, max_length=100)
    type_en = gis_models.CharField(null=True, blank=True, max_length=100)
    code_local = gis_models.CharField(null=True, blank=True, max_length=100)
    code_hasc = gis_models.CharField(null=True, blank=True, max_length=100)
    note = gis_models.TextField(null=True, blank=True)
    hasc_maybe = gis_models.CharField(null=True, blank=True, max_length=100)
    region = gis_models.CharField(null=True, blank=True, max_length=100)
    region_cod = gis_models.CharField(null=True, blank=True, max_length=100)
    provnum_ne = gis_models.IntegerField(null=True, blank=True)
    gadm_level = gis_models.IntegerField(null=True, blank=True)
    check_me = gis_models.IntegerField(null=True, blank=True)
    scalerank = gis_models.IntegerField(null=True, blank=True)
    datarank = gis_models.IntegerField(null=True, blank=True)
    abbrev = gis_models.CharField(null=True, blank=True, max_length=100)
    postal = gis_models.CharField(null=True, blank=True, max_length=100)
    area_sqkm = gis_models.CharField(null=True, blank=True, max_length=100)
    sameascity = gis_models.IntegerField(null=True, blank=True)
    labelrank = gis_models.IntegerField(null=True, blank=True)
    featurecla = gis_models.CharField(null=True, blank=True, max_length=100)
    name_len = gis_models.IntegerField(null=True, blank=True)
    mapcolor9 = gis_models.IntegerField(null=True, blank=True)
    mapcolor13 = gis_models.IntegerField(null=True, blank=True)
    fips = gis_models.CharField(null=True, blank=True, max_length=100)
    fips_alt = gis_models.CharField(null=True, blank=True, max_length=100)
    woe_id = gis_models.IntegerField(null=True, blank=True)
    woe_label = gis_models.CharField(null=True, blank=True, max_length=100)
    woe_name = gis_models.CharField(null=True, blank=True, max_length=100)
    center_location = gis_models.PointField(null=True, blank=True)
    sov_a3 = gis_models.CharField(null=True, blank=True, max_length=3)
    adm0_a3 = gis_models.CharField(null=True, blank=True, max_length=3)
    adm0_label = gis_models.IntegerField(null=True, blank=True)
    admin = gis_models.CharField(null=True, blank=True, max_length=100)
    geonunit = gis_models.CharField(null=True, blank=True, max_length=100)
    gu_a3 = gis_models.CharField(null=True, blank=True, max_length=3)
    gn_id = gis_models.IntegerField(null=True, blank=True)
    gn_name = gis_models.CharField(null=True, blank=True, max_length=100)
    gns_id = gis_models.IntegerField(null=True, blank=True)
    gns_name = gis_models.CharField(null=True, blank=True, max_length=100)
    gn_level = gis_models.IntegerField(null=True, blank=True)
    gn_region = gis_models.CharField(null=True, blank=True, max_length=100)
    gn_a1_code = gis_models.CharField(null=True, blank=True, max_length=100)
    region_sub = gis_models.CharField(null=True, blank=True, max_length=100)
    sub_code = gis_models.CharField(null=True, blank=True, max_length=100)
    gns_level = gis_models.IntegerField(null=True, blank=True)
    gns_lang = gis_models.CharField(null=True, blank=True, max_length=100)
    gns_adm1 = gis_models.CharField(null=True, blank=True, max_length=100)
    gns_region = gis_models.CharField(null=True, blank=True, max_length=100)
    polygon = gis_models.TextField(null=True, blank=True)
    geometry_type = gis_models.CharField(null=True, blank=True, max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "admin1 regions"


