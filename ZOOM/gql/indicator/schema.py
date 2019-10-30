from django.db.models import Q
from django_filters import CharFilter, FilterSet, NumberFilter
from graphene import Boolean, Int, List, String, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphene

from gql.utils import AggregationNode, StringListFilter
from indicator.models import Datapoints, FilterHeadings, Filters, Indicator


class IndicatorNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = Indicator
        interfaces = (relay.Node, )

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class IndicatorFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')
    file__entry_id = NumberFilter(method='filter_file__entry_id')
    file__entry_id__in = CharFilter(method='filter_file__entry_id__in')
    year__range = CharFilter(method='filter_year__range')
    country__iso2 = CharFilter(method='filter_country__iso2')
    fileSource__name__in = StringListFilter(method='file_source__name__in')

    class Meta:
        model = Indicator
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith'],
            'file_source__name': ['exact'],
            'file__accessibility': ['exact', 'in'],
            'file__title': ['exact', 'in']
        }

    def filter_country__iso2(self, queryset, name, value):
        # Oke so we do this nonsesne of converting the query set to
        # a sorts of id list, because, this filter happens after the year range
        # and apperantly because the year_range uses a deep relation filter
        # and distinct it makes this query insanely slow,
        # even though the object
        # count of that query is lower than the object count of 'objects.all()'
        # with which this filter works fine, so i assume the distinct function
        # here is causing the query set to lag,
        # so for now we use this work around
        # which actually works, #JustDjangoThings
        ids = queryset.values_list('id')
        # 1) country__iso2=value -
        # so here we want to filter by the country association saved in the
        # indicator model, mainly the subnational, postcode, province etc.
        # relation with a country is saved in the indicator, and i'm not
        # redoing it(#Morty) cause this approach has been done and
        # it might be more optimal then doing
        # relation checks over relation checks
        # over relation checks
        # 2) datapoints__geolocation__type='pointbased' -
        # We also want to retrieve all of the point based data, cause they are
        # unnasociated with specific countries, but they might be the ones
        # that the user wants to map in their kenya/NL focus pages
        # 3) datapoints__geolocation__country__iso2=value -
        # and here we actually filter the indicators which datapoints
        # which have been mapped out by country, have the specified
        # country
        return Indicator.objects.filter(
            Q(id__in=ids) & Q(
                Q(country__iso2=value) |
                Q(datapoints__geolocation__type='pointbased') |
                Q(datapoints__geolocation__country__iso2=value))
        ).distinct()

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})

    def filter_file__entry_id(self, queryset, name, value):
        return queryset.filter(file__id=value)

    def filter_file__entry_id__in(self, queryset, name, value):
        value_list = value.split(',')
        # so with this tweek of filtering doesnt
        # matter what file ids are passed in we
        # always return the public indicators
        return queryset.filter(
            Q(file__id__in=value_list) | Q(file__accessibility='a')
        )

    def filter_year__range(self, queryset, name, value):
        return queryset.filter(
            datapoints__date__gte=value.split(',')[0],
            datapoints__date__lte=value.split(',')[1]
        ).distinct()

    def file_source__name__in(self, queryset, name, value):
        name = 'file_source__name__in'
        return queryset.filter(**{name: value})


class DatapointsAggregationNode(AggregationNode):
    value = graphene.Float()
    valueFormatType = graphene.String()
    date = graphene.String()
    comment = graphene.String()
    indicatorName = graphene.String()
    indicatorDescription = graphene.String()
    geolocationTag = graphene.String()
    geolocationIso2 = graphene.String()
    geolocationIso3 = graphene.String()
    geolocationObjectId = graphene.Int()
    geolocationContentObject = graphene.String()
    geolocationType = graphene.String()
    filterName = graphene.String()
    filterId = graphene.Int()
    indicatorFilterHeadingName = graphene.String()
    indicatorFilterHeadingId = graphene.Int()
    geolocationCenterLongLat = graphene.JSONString()
    geolocationPolygons = graphene.JSONString()
    tileUrl = graphene.String()
    zoom = graphene.Int()
    uniqCount = graphene.Int()
    minValue = graphene.Int()
    maxValue = graphene.Int()

    Model = Datapoints

    FIELDS_MAPPING = {
        'value': 'value',
        'valueFormatType': 'value_format__type',
        'date': 'date',
        'comment': 'comment',
        'indicatorName': 'indicator__name',
        'indicatorDescription': 'indicator__description',
        'geolocationTag': 'geolocation__tag',
        'geolocationIso2': 'geolocation__iso2',
        'geolocationIso3': 'geolocation__iso3',
        'geolocationObjectId': 'geolocation__object_id',
        'geolocationContentObject': 'geolocation__content_object',
        'geolocationType': 'geolocation__type',
        'filterName': 'filters__name',
        'filterId': 'filters__id',
        'indicatorFilterHeadingName': 'indicator__filterheadings__name',
        'indicatorFilterHeadingId': 'indicator__filterheadings__id',
        'geolocationCenterLongLat': 'geolocation__center_longlat',
        'geolocationPolygons': 'geolocation__polygons',
    }

    FIELDS_FILTER_MAPPING = {
        'value': 'value',
        'valueFormatType': 'value_format__type',
        'date': 'date',
        'comment': 'comment',
        'indicatorName': 'indicator__name',
        'indicatorDescription': 'indicator__description',
        'geolocationTag__In': 'geolocation__tag__in',
        'geolocationIso2__In': 'geolocation__iso2__in',
        'geolocationIso3__In': 'geolocation__iso3__in',
        'geolocationObjectId__In': 'geolocation__object_id__in',
        'geolocationContentObject__In': 'geolocation__content_object__in',
        'geolocationType__In': 'geolocation__type__in',
        'filterId__In': 'filters__id__in',
        'indicatorFilterHeadingId__In': 'indicator__filterheading__id__in',
        # TODO: create test for below filed filter
        'date__In': 'date__in',
        'filterName__In': 'filters__name__in',
        'indicatorName__In': 'indicator__name__in',
        'geolocationIso2__Is__Null': 'geolocation__iso2__isnull',
        'geolocationIso3__Is__Null': 'geolocation__iso3__isnull',
        'indicatorId__In': 'indicator__id__in',
        'indicator_file_accesibility': 'indicator__file__accessibility'
    }

    # OR filter
    # (a = 1 OR a = Null)
    # Should be had the same field is on filter too.
    # This can not use as a stand alone filter
    # Can not -> (a = null) should be -> (a = 1 OR a = Null)
    FIELDS_OR_FILTER_MAPPING = {
        'OR__Geolocation_Iso2__Is__Null': 'geolocation__iso2__isnull',
        'OR__Geolocation_Iso3__Is__Null': 'geolocation__iso3__isnull',
    }
    #  Remove filter related to or_filter on the filter fields
    FIELD_OR_RELATED_MAPPING = {
        'OR__Geolocation_Iso2__Is__Null': 'geolocation__iso2__in',
        'OR__Geolocation_Iso3__Is__Null': 'geolocation__iso3__in',
    }


class FilterHeadingsNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = FilterHeadings
        interfaces = (relay.Node,)

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class FilterHeadingsFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = FilterHeadings
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith'],
            'indicator': ['exact', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class DatapointsNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = Datapoints
        interfaces = (relay.Node,)

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class DatapointsFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = Datapoints
        fields = {
            'metadata': ['exact', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class FiltersNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = Filters
        interfaces = (relay.Node, )

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class FiltersFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id_in')
    indicator_id = NumberFilter(method='filter_indicator_id')
    indicator_id__in = CharFilter(method='filter_indicator_id_in')

    class Meta:
        model = Filters
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith'],
            'metadata': ['exact', 'in'],
            'indicator__name': ['exact', 'in'],
            'heading__id': ['exact', 'in'],
            'heading__name': ['exact', 'in']
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id_in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})

    def filter_indicator_id(self, queryset, name, value):
        name = 'indicator__id'
        return queryset.filter(**{name: value})

    def filter_indicator_id_in(self, queryset, name, value):
        name = 'indicator__id__in'
        return queryset.filter(**{name: eval(value)})


class Query(object):
    indicator = relay.Node.Field(IndicatorNode)
    all_indicators = DjangoFilterConnectionField(
        IndicatorNode, filterset_class=IndicatorFilter
    )

    datapoints_aggregation = graphene.List(
        DatapointsAggregationNode,
        groupBy=List(of_type=String),
        fields=List(of_type=String),
        orderBy=List(of_type=String),
        aggregation=List(of_type=String),
        geolocationTag__In=List(of_type=String),
        geolocationIso2__In=List(of_type=String),
        geolocationIso3__In=List(of_type=String),
        geolocationObjectId__In=List(of_type=String),
        geolocationContentObject__In=List(of_type=String),
        geolocationType__In=List(of_type=String),
        filterId__In=List(of_type=Int),
        indicatorFilterHeadingId__In=List(of_type=Int),
        date__In=List(of_type=String),
        filterName__In=List(of_type=String),
        indicatorName__In=List(of_type=String),
        indicatorId__In=List(of_type=Int),
        geolocationIso2__Is__Null=Boolean(),
        geolocationIso3__Is__Null=Boolean(),
        OR__Geolocation_Iso2__Is__Null=Boolean(),
        OR__Geolocation_Iso3__Is__Null=Boolean(),
        unique_indicator=Boolean(),
        indicator_file_accesibility=String(),
        tileUrl=Boolean(),
        currentTiles=String()
    )

    all_filter_headings = DjangoFilterConnectionField(
        FilterHeadingsNode, filterset_class=FilterHeadingsFilter
    )

    all_data_points = DjangoFilterConnectionField(
        DatapointsNode, filterset_class=DatapointsFilter
    )

    all_filters = DjangoFilterConnectionField(
        FiltersNode, filterset_class=FiltersFilter
    )

    def resolve_datapoints_aggregation(self, context, **kwargs):
        return DatapointsAggregationNode().get_nodes(context, **kwargs)
