import graphene
from graphene import relay, List, String, Int
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, NumberFilter, CharFilter

from gql.utils import AggregationNode
from indicator.models import (
    Indicator,
    Datapoints,
    FilterHeadings,
    Filters
)


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

    class Meta:
        model = Indicator
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith'],
            'file_source': ['exact', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


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
        'indicatorFilterHeadingId': 'indicator__filterheadings__id'
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
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = Filters
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith'],
            'metadata': ['exact', 'in'],
            'indicator__name' :['exact', 'in'],
            'indicator__id': ['exact', 'in'],
            'heading__id': ['exact', 'in'],
            'heading__name': ['exact', 'in']
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class Query(object):
    indicator = relay.Node.Field(IndicatorNode)
    all_indicators = DjangoFilterConnectionField(
        IndicatorNode, filterset_class=IndicatorFilter
    )

    datapoints_aggregation = graphene.List(
        DatapointsAggregationNode,
        groupBy=List(of_type=String),
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
