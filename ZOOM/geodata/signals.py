from django.db.models import signals
from django.dispatch import receiver

from geodata.models import (
    Geolocation, Country, City, Region,
    SubNational, PointBased, Province, PostCode
)


@receiver(signals.post_save, sender=Geolocation)
def geolocation_post_save(sender, instance, **kwargs):
    is_diff = False
    if instance.type == 'country':
        country = Country.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != country.center_longlat or\
                instance.polygons != country.polygons or \
                instance.iso2 != country.iso2 or\
                instance.iso3 != country.iso3:
            instance.center_longlat = country.center_longlat
            instance.polygons = country.polygons
            instance.iso2 = country.iso2
            instance.iso3 = country.iso3
            is_diff = True
    elif instance.type == 'region':
        region = Region.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != region.center_longlat or\
                instance.polygons != region.polygons or\
                instance.iso3 != region.code:
            instance.center_longlat = region.center_longlat
            instance.polygons = region.polygons
            instance.iso2 = ''
            instance.iso3 = region.code
            is_diff = True
    elif instance.type == 'subnational':
        sub_national = SubNational.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != sub_national.center_longlat or\
                instance.polygons != sub_national.polygons or\
                instance.iso3 != sub_national.iso_3166_2:
            instance.center_longlat = sub_national.center_longlat
            instance.polygons = sub_national.polygons
            instance.iso2 = ''
            instance.iso3 = sub_national.iso_3166_2
            is_diff = True
    elif instance.type == 'city':
        city = City.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != city.center_longlat or\
                instance.polygons != city.polygons:
            instance.center_longlat = city.center_longlat
            instance.polygons = city.polygons
            instance.iso2 = ''
            instance.iso3 = ''
            is_diff = True
    elif instance.type == 'pointbased':
        point_based = PointBased.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != point_based.center_longlat:
            instance.center_longlat = point_based.center_longlat
            instance.iso2 = ''
            instance.iso3 = ''
            is_diff = True
    elif instance.type == 'province':
        province = Province.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != province.center_longlat or\
                instance.polygons != province.polygons:
            instance.center_longlat = province.center_longlat
            instance.polygons = province.polygons
            instance.iso2 = ''
            instance.iso3 = ''
            is_diff = True
    elif instance.type == 'postcode':
        postcode = PostCode.objects.get(id=instance.object_id)
        if kwargs.get('created') or\
                instance.center_longlat != postcode.center_longlat or\
                instance.polygons != postcode.polygons:
            instance.center_longlat = postcode.center_longlat
            instance.polygons = postcode.polygons
            instance.iso2 = ''
            instance.iso3 = ''
            is_diff = True

    if is_diff:
        instance.save()
