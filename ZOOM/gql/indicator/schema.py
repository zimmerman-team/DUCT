import graphene
from graphene import relay, List, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, NumberFilter, CharFilter

from gql.utils import AggregationNode
from indicator.models import Indicator, Datapoints


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
        'geolocation__type': 'geolocation__type',
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
    }


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
    )

    def resolve_datapoints_aggregation(self, context, **kwargs):
        return DatapointsAggregationNode().get_nodes(context, **kwargs)
