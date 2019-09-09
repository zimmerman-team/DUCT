import factory
from django.contrib.gis.geos import GEOSGeometry, Point

from geodata import models
from metadata import models as metadata_models


class NoDatabaseFactory(factory.django.DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class CountryFactory(NoDatabaseFactory):
    class Meta:
        model = models.Country

    name = 'Afghanistan'
    center_longlat = Point(1, 3)
    polygons = GEOSGeometry('{"type":"Polygon","coordinates":'
                            '[[[29.339997592900346,-4.499983412294092],'
                            '[29.276383904749053,-3.293907159034063],'
                            '[29.024926385216787,-2.839257907730158],'
                            '[29.632176141078588,-2.917857761246097],'
                            '[29.938359002407942,-2.348486830254238],'
                            '[30.469696079232985,-2.413857517103458],'
                            '[30.527677036264464,-2.807631931167535],'
                            '[30.7430127296247,-3.034284763199686],'
                            '[30.75226281100495,-3.35932952231557],'
                            '[30.505559523243566,-3.568567396665365],'
                            '[30.116332635221173,-4.090137627787243],'
                            '[29.753512404099922,-4.452389418153281],'
                            '[29.339997592900346,-4.499983412294092]]]}}')


class GeolocationFactory(NoDatabaseFactory):
    class Meta:
        model = models.Geolocation
        django_get_or_create = ('iso2',)


    tag = 'asia'
    iso2 = ''
    iso3 = ''
    type='region'
    object_id = 4
    content_type_id = 15


class RegionFactory(NoDatabaseFactory):
    class Meta:
        model = models.Region

    name = 'asia'
    center_longlat = Point(1, 5)
    polygons = GEOSGeometry('{ "type": "MultiPolygon","coordinates": '
                            '[[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], '
                            '[102.0, 3.0], [102.0, 2.0]]],'
                            '[[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], '
                            '[100.0, 1.0], [100.0, 0.0]],'
                            '[[100.2, 0.2], [100.8, 0.2], [100.8, 0.8],'
                            ' [100.2, 0.8], [100.2, 0.2]]]]}')


class CityFactory(NoDatabaseFactory):
    class Meta:
        model = models.City

    name = 'london'


class FileSourceFactory(NoDatabaseFactory):
    class Meta:
        model = metadata_models.FileSource

    name = 'dummy_file_source'


class FileFactory(NoDatabaseFactory):
    class Meta:
        model = metadata_models.File
