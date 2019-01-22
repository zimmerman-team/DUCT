from django.db.models import signals
from django.dispatch import receiver

from geodata.models import Geolocation, Country, City, Region, \
    SubNational, PointBased


@receiver(signals.post_save, sender=Geolocation)
def geolocation_post_save(sender, instance, **kwargs):
    is_diff = False
    if instance.type == 'country':
        country = Country.objects.get(id=instance.object_id)
        if instance.center_longlat != country.center_longlat or \
                kwargs.get('created'):
            is_diff = True
            instance.center_longlat = country.center_longlat

        if instance.polygons != country.polygons or \
                kwargs.get('created'):
            is_diff = True
            instance.polygons = country.polygons
    elif instance.type == 'region':
        region = Region.objects.get(id=instance.object_id)
        if instance.center_longlat != region.center_longlat or \
                kwargs.get('created'):
            is_diff = True
            instance.center_longlat = region.center_longlat

        if instance.polygons != region.polygons or \
                kwargs.get('created'):
            is_diff = True
            instance.polygons = region.polygons
    elif instance.type == 'subnational':
        sub_national = SubNational.objects.get(id=instance.object_id)
        if instance.center_longlat != sub_national.center_longlat or \
                kwargs.get('created'):
            is_diff = True
            instance.center_longlat = sub_national.center_longlat

        if instance.polygons != sub_national.polygons or \
                kwargs.get('created'):
            is_diff = True
            instance.polygons = sub_national.polygons
    elif instance.type == 'city':
        city = City.objects.get(id=instance.object_id)
        if instance.center_longlat != city.center_longlat or \
                kwargs.get('created'):
            is_diff = True
            instance.center_longlat = city.center_longlat
            instance.polygons = None
    elif instance.type == 'pointbased':
        point_based = PointBased.objects.get(id=instance.object_id)
        if instance.center_longlat != point_based.center_longlat or \
                kwargs.get('created'):
            is_diff = True
            instance.center_longlat = point_based.center_longlat
            instance.polygons = None

    if is_diff:
        instance.save()
