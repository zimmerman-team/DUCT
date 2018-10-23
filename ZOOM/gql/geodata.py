import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, NumberFilter, CharFilter

from geodata.models import Geolocation, Country


class CountryNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = Country
        only_fields = (
            'iso2', 'iso3', 'name'
        )
        interfaces = (relay.Node, )

    def resolve_this_id(self, context, **kwargs):
        return self.country_id


class CountryFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = Country
        fields = {
            'iso2': ['exact', 'icontains', 'istartswith', 'in'],
            'iso3': ['exact', 'icontains', 'istartswith', 'in'],
            'name': ['exact', 'icontains', 'istartswith', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'country_id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'country_id__in'
        return queryset.filter(**{name: eval(value)})


class GeolocationNode(DjangoObjectType):
    entry_id = graphene.String()
    country = graphene.Field(CountryNode)

    class Meta:
        model = Geolocation
        interfaces = (relay.Node,)

    def resolve_entry_id(self, context, **kwargs):
        return self.geolocation_id

    def resolve_country(self, context, **kwargs):
        return Country.objects.get(country_id=self.object_id) \
            if self.type == "country" else None


class GeolocatioFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = Geolocation
        fields = {
            'geolocation_id': ['exact', 'in'],
            'tag': ['exact', 'icontains', 'istartswith', 'in'],
            'object_id': ['exact', 'in'],
            'type': ['exact', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'geolocation_id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'geolocation_id__in'
        return queryset.filter(**{name: eval(value)})


class Query(object):
    country = relay.Node.Field(CountryNode)
    all_countries = DjangoFilterConnectionField(
        CountryNode, filterset_class=CountryFilter
    )

    gelocation = relay.Node.Field(GeolocationNode)
    all_gelocations = DjangoFilterConnectionField(
        GeolocationNode, filterset_class=GeolocatioFilter
    )
