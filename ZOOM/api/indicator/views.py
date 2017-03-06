from rest_framework.filters import DjangoFilterBackend

from api.generics.views import DynamicListView

from api.indicator.serializers import *

from indicator.models import IndicatorDatapoint

from api.indicator.filters import IndicatorDataFilter

from api.aggregation.views import AggregationView, Aggregation, GroupBy

from django.db.models import Count, Sum, F

class IndicatorDataList(DynamicListView):

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
    )
