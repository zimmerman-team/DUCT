from django.contrib.gis.geos import Point
import factory
from geodata import models



class NoDatabaseFactory(factory.django.DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class CountryFactory(NoDatabaseFactory):
    class Meta:
        model = models.Country

    name = 'Afghanistan'
    center_longlat = Point(1, 3)


class GeolocationFactory(NoDatabaseFactory):
    class Meta:
        model = models.Geolocation


    tag = 'Albania'
    iso2 = 'al'
    iso3 = 'alb'
    object_id = 4
    content_type_id = 15

class CityFactory(NoDatabaseFactory):
    class Meta:
        model = models.City

    geoname_id = 1000
    name = 'london'
    location = Point(5, 23)

