import graphene
from graphene import Boolean, Int, List, String
from graphene_django.filter import DjangoFilterConnectionField

import gql.indicator.schema
from gql.indicator.schema import (DatapointsAggregationNode, IndicatorFilter,
                                  IndicatorNode)

# NOTE: this is really hard code if want to filter with other option
# or other filter for public endpoint please add or change here
# in the below code


class IndicatorPublicFilter(IndicatorFilter):

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):

        # Filter only for indicator with file has 'a' accessibility
        if queryset is None:
            queryset = self._meta.model._default_manager.filter(
                file__accessibility='a'
            )
        else:
            queryset = queryset.filter(file__accessibility='a')

        super(IndicatorPublicFilter, self).__init__(
            data=data, queryset=queryset, request=request, prefix=prefix
        )


class DatapointsAggregationPublicNode(DatapointsAggregationNode):

    def get_filters(self, context, **kwargs):
        filters = super(DatapointsAggregationPublicNode, self).get_filters(
            context, **kwargs
        )

        # Filter only for indicator with file has 'a' accessibility
        filters['indicator__file__accessibility'] = 'a'

        return filters


class Query(gql.indicator.schema.Query):
    all_indicators = DjangoFilterConnectionField(
        IndicatorNode, filterset_class=IndicatorPublicFilter
    )

    datapoints_aggregation = graphene.List(
        DatapointsAggregationPublicNode,
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
        geoJsonUrl=Boolean(),
        currentGeoJson=String()
    )

    def resolve_datapoints_aggregation(self, context, **kwargs):
        return DatapointsAggregationPublicNode().get_nodes(context, **kwargs)
