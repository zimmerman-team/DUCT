from django.db.models import Count, Sum, F
from django.db.models import FloatField
from django.db.models.functions import Cast
from rest_framework.filters import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView, GenericAPIView, ListAPIView

from indicator.models import IndicatorDatapoint
from api.indicator.serializers import *
from api.indicator.filters import IndicatorDataFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from api.generics.views import DynamicListView


class IndicatorDataList(ListAPIView):

    queryset = IndicatorDatapoint.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = IndicatorDataFilter
    serializer_class = IndicatorSerializer

    fields = (
        'id',
        'file',
        'date_format',
        'indicator_category',
        'indicator',
        'country',
        'date_value',
        'source',
        'measure_value',
        'unit_of_measure'
        'other',
    )


def annotate_measure(query_params, groupings):

    annotation_components = F('measure_value')

    return Sum(Cast(annotation_components, FloatField()))


class IndicatorDataAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - thingiemahbob

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count`
    - `count_distinct`

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = IndicatorDatapoint.objects.all()

    filter_backends = (DjangoFilterBackend,)
    filter_class = IndicatorDataFilter

    allowed_aggregations = (
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        ),
        Aggregation(
            query_param='count_distinct',
            field='count',
            annotate=Count('id', distinct=True),
        ),
        Aggregation(
            query_param='measure_value',
            field='total_measure',
            annotate=annotate_measure,
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="indicator_category",
            fields="indicator_category",
        ),
        GroupBy(
            query_param="indicator",
            fields="indicator",
        ),
        GroupBy(
            query_param="date_value",
            fields="date_value",
        ),
        GroupBy(
            query_param="country",
            fields="country",
        ),
        GroupBy(
            query_param="country__region",
            fields="country__region",
        ),
        GroupBy(
            query_param="country__name",
            fields="country__name",
        ),
        GroupBy(
            query_param="country__region__name",
            fields="country__region__name"
        ),
        GroupBy(
            query_param="unit_of_measure",
            fields="unit_of_measure",
        ),        
    )
