from django.db.models import Count, Sum, F, Avg, Max, Min
from django.db.models import FloatField
from django.db.models.functions import Cast
from rest_framework.filters import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView, GenericAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from file_upload.models import File
from indicator.models import IndicatorDatapoint, Indicator, IndicatorCategory
from api.indicator.serializers import IndicatorSerializer, IndicatorDataSerializer, IndicatorCategorySerializer
from api.indicator.filters import IndicatorFilter, IndicatorDataFilter, IndicatorCategoryDataFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from api.generics.views import DynamicListView


@api_view(['POST'])
def reset_mapping(request):
    file = File.objects.get(id=request.data['file_id'])
    indicators = IndicatorDatapoint.objects.filter(file=file)
    #foreign keys 

    indicators.delete()
    return Response({"success":1})


class IndicatorList(ListAPIView):
    queryset = IndicatorDatapoint.objects.filter(file__authorised = True).values("indicator").distinct() #Indicator.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = IndicatorFilter
    serializer_class = IndicatorSerializer

    fields = (
        'id',
        'description'
    )


class IndicatorDataList(ListAPIView):

    queryset = IndicatorDatapoint.objects.filter(file__authorised = True)
    filter_backends = (DjangoFilterBackend, )
    filter_class = IndicatorDataFilter
    serializer_class = IndicatorDataSerializer

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
        'unit_of_measure',
        'other',
    )

    # def get_queryset(self):
    #     if self.request.data.get('group_by') is None:
    #         return IndicatorDatapoint.objects.none()
    #     return IndicatorDatapoint.objects.all()

'''
Data Post Example:

# Without date_value filter:

{
            "indicator_x" : "Bananas",
            "indicator_category_x" : "Area Harvested",
            "indicator_y" : "Pigs",
            "indicator_category_y": "Stocks"
}

# With date_value filter:

{
            "indicator_x" : "Bananas",
            "indicator_category_x" : "Area Harvested",
            "indicator_y" : "Pigs",
            "indicator_category_y": "Stocks",
            "date_value": "2004"
}
'''

class IndicatorCategoryDataList(ListAPIView):

    ind = IndicatorDatapoint.objects.filter(file__authorised = True).values("indicator").distinct()
    queryset = IndicatorCategory.objects.filter(indicator__in = ind)
    #queryset = IndicatorCategory.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = IndicatorCategoryDataFilter
    serializer_class = IndicatorCategorySerializer
    #pagination_class = None

    fields = (
        'id',
        'unique_identifier',
        'name',
        'level',
        'child',
        'indicator',
    )


def annotate_measure(query_params, groupings):

    annotation_components = F('measure_value')

    return Sum(Cast(annotation_components, FloatField()))

def mean_measure(query_params, groupings):

    annotation_components = F('measure_value')

    return Avg(Cast(annotation_components, FloatField()))

def max_measure(query_params, groupings):

    annotation_components = F('measure_value')

    return Max(Cast(annotation_components, FloatField()))

def min_measure(query_params, groupings):

    annotation_components = F('measure_value')

    return Min(Cast(annotation_components, FloatField()))


class IndicatorDataAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:
    
    - `indicator_category`
    - `indicator`
    - `date_value`
    - `country`
    - `country__region`
    - `country__name`
    - `country__region__name`
    - `unit_of_measure`

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:


    - `count`
    - `count_distinct`
    - `measure_value`
    - `mean_value`
    - `max_value`
    - `min_value`

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = IndicatorDatapoint.objects.filter(file__authorised = True)

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
        Aggregation(
              query_param='mean_value',
            field='total_measure',
            annotate=mean_measure,
        ),
        Aggregation(
            query_param='max_value',
            field='total_measure',
            annotate=max_measure,
        ),
        Aggregation(
            query_param='min_value',
            field='total_measure',
            annotate=min_measure,
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="indicator_category",
            fields=("indicator_category_id", "indicator_category__name", "indicator_category__level"),
        ),
        GroupBy(
            query_param="indicator",
            fields=("indicator", "file__data_source__name"),
            # renamed_fields=("indicator", "source"),
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
