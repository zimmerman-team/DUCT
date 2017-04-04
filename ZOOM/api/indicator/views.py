from rest_framework.filters import DjangoFilterBackend

from api.generics.views import DynamicListView

from rest_framework.generics import RetrieveAPIView, GenericAPIView, ListAPIView

from api.indicator.serializers import *

from indicator.models import IndicatorDatapoint

from api.indicator.filters import IndicatorDataFilter

from api.aggregation.views import AggregationView, Aggregation, GroupBy

from django.db.models import Count, Sum, F

from django.db.models import FloatField
from django.db.models.functions import Cast

class IndicatorDataList(ListAPIView):

    queryset = IndicatorDatapoint.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = IndicatorDataFilter
    serializer_class = IndicatorSerializer

    fields = (
        'id',
        'file_source_id',
        'date_format_id',
        'indicator_category_id',
        'indicator_id',
        'country_id',
        'date_value',
        'source_id',
        'measure_value',
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
            query_param="indicator_category_id",
            fields="indicator_category_id",
        ),
        GroupBy(
            query_param="indicator_id",
            fields="indicator_id",
        ),
        GroupBy(
            query_param="date_value",
            fields="date_value",
        ),
        GroupBy(
            query_param="country_id",
            fields="country_id",
        ),
        GroupBy(
            query_param="country_id__region",
            fields="country_id__region",
        ),
        GroupBy(
            query_param="country_id__name",
            fields="country_id__name",
        ),
        GroupBy(
            query_param="country_id__region__name",
            fields="country_id__region__name",
        ),
    )
