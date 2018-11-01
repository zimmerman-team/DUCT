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
