import graphene
from django_filters import FilterSet, NumberFilter
from graphene import relay, List, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from indicator.models import Indicator, IndicatorCategory, IndicatorDatapoint
from geodata.models import Country
from gql.utils import AggregationNode


class IndicatorNode(DjangoObjectType):
    this_id = graphene.String()

    class Meta:
        model = Indicator
        filter_fields = {
            'id': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )

    def resolve_this_id(self, context, **kwargs):
        return self.id


class IndicatorFilter(FilterSet):
    this_id = NumberFilter(method='filter_this_id')

    class Meta:
        model = Indicator
        fields = {
            'description': ['exact', 'icontains', 'istartswith'],
            'count': ['gte', 'lte']
        }


class IndicatorCategoryNode(DjangoObjectType):
    this_id = graphene.Int()

    class Meta:
        model = IndicatorCategory
        interfaces = (relay.Node, )

    def resolve_this_id(self, context, **kwargs):
        return self.id


class IndicatorCategoryFilter(FilterSet):
    this_id = NumberFilter(method='filter_this_id')

    class Meta:
        model = IndicatorCategory
        fields = {
            'unique_identifier': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            'code': ['exact'],
            'level': ['exact'],
            'indicator': ['exact'],
            'indicator__description': ['exact', 'icontains', 'istartswith'],
        }

    def filter_this_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})


class CountryNode(DjangoObjectType):
    this_id = graphene.Int()

    class Meta:
        model = Country
        filter_fields = {
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains'],
        }
        only_fields = (
            'code', 'numerical_code_un', 'name', 'region', 'polygon'
        )
        interfaces = (relay.Node, )

    def resolve_this_id(self, context, **kwargs):
        return self.id


class IndicatorDatapointNode(DjangoObjectType):
    this_id = graphene.Int()

    class Meta:
        model = IndicatorDatapoint
        only_fields = (
            'filter', 'date_created', 'date_format', 'indicator',
            'indicator_category', 'unit_of_measure', 'country', 'date_value',
            'source', 'measure_value', 'other'
        )
        interfaces = (relay.Node, )

    def resolve_this_id(self, context, **kwargs):
        return self.id


class IndicatorDatapointFilter(FilterSet):
    this_id = NumberFilter(method='filter_this_id')

    class Meta:
        model = IndicatorDatapoint
        fields = {
            'measure_value': ['exact'],
        }

    def filter_this_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})


class IndicatorDatapointAggregationNode(AggregationNode):
    indicatorCount = graphene.Float()
    indicatorCategoryName = graphene.String()
    countryCode = graphene.String()
    countryName = graphene.String()

    Model = IndicatorDatapoint

    FIELDS_MAPPING = {
        'indicatorCount': 'indicator__count',
        'indicatorCategoryName': 'indicator_category__name',
        'countryCode': 'country__code',
        'countryName': 'country__name'
    }

    FIELDS_FILTER_MAPPING = {
        'indicatorCount': 'indicator__count',
        'indicatorCategoryName': 'indicator_category__name',
        'countryCode': 'country__code',
        'countryName': 'country__name'
    }


class Query(object):
    indicator_category = relay.Node.Field(IndicatorCategoryNode)
    all_indicator_categories = DjangoFilterConnectionField(
        IndicatorCategoryNode, filterset_class=IndicatorCategoryFilter
    )

    indicator = relay.Node.Field(IndicatorNode)
    all_indicators = DjangoFilterConnectionField(
        IndicatorNode, filterset_class=IndicatorFilter
    )

    country = relay.Node.Field(CountryNode)
    all_countries = DjangoFilterConnectionField(
        CountryNode
    )

    indicator_datapoint = relay.Node.Field(IndicatorDatapointNode)
    all_indicator_datapoints = DjangoFilterConnectionField(
        IndicatorDatapointNode, filterset_class=IndicatorDatapointFilter
    )

    indicator_datapoint_aggregation = graphene.List(
        IndicatorDatapointAggregationNode,
        groupBy=List(of_type=String),
        orderBy=List(of_type=String),
        aggregation=List(of_type=String),
        indicatorCategoryName=List(of_type=String))

    def resolve_indicator_datapoint_aggregation(self, context, **kwargs):
        return IndicatorDatapointAggregationNode().get_nodes(context, **kwargs)
