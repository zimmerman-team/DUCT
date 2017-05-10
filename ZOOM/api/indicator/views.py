from django.db.models import Count, Sum, F
from django.db.models import FloatField
from django.db.models.functions import Cast
from rest_framework.filters import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView, GenericAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.file.views import update_status
from indicator.models import IndicatorDatapoint, Indicator, IndicatorCategory
from api.indicator.serializers import *
from api.indicator.filters import IndicatorDataFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from api.generics.views import DynamicListView


@api_view(['POST'])
def reset_mapping(request):
    file = File.objects.get(id=request.data['file_id'])
    indicators = IndicatorDatapoint.objects.filter(file=file)
    #foreign keys 

    indicators.delete()
    return Response({"success":1})

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

class ScatterPlotDataList(APIView):
    def post(self, request):
        if request.method == 'POST':
            indicator_x = request.data.get('indicator_x')
            indicator_category_x = request.data.get('indicator_category_x')
            indicator_y = request.data.get('indicator_y')
            indicator_category_y = request.data.get('indicator_category_y')
            date_value = request.data.get('date_value')
        else:
            return Response("No data posted")
        indicator_obj_x = Indicator.objects.get(id=indicator_x)
        indicator_category_obj_x = IndicatorCategory.objects.get(id=indicator_category_x)
        indicator_obj_y = Indicator.objects.get(id=indicator_y)
        indicator_category_obj_y = IndicatorCategory.objects.get(id=indicator_category_y)
        if date_value:
            initial_items = IndicatorDatapoint.objects.filter(
                indicator=indicator_obj_x,
                indicator_category=indicator_category_obj_x,
                date_value=date_value
                )
        else:
            initial_items = IndicatorDatapoint.objects.filter(
                indicator=indicator_obj_x,
                indicator_category=indicator_category_obj_x
                )
        results = []
        for item in initial_items:
            date_value = item.date_value
            country = item.country
            if country and date_value:
                code = country.code
                if date_value:
                    new_items = IndicatorDatapoint.objects.filter(
                        indicator=indicator_obj_y,
                        indicator_category=indicator_category_obj_y,
                        country=country,
                        date_value=date_value
                        )
                else:
                    new_items = IndicatorDatapoint.objects.filter(
                        indicator=indicator_obj_y,
                        indicator_category=indicator_category_obj_y,
                        country=country
                        )
                if new_items.count() > 0 :
                    for new_item in new_items:
                        result = {
                            "date_value": date_value,
                            "country": code,
                            "indicator_x": indicator_x,
                            "indicator_category_x": indicator_category_x,
                            "measure_value_x": float(item.measure_value),
                            "indicator_y": indicator_y,
                            "indicator_category_y": indicator_category_y,
                            "measure_value_y": float(new_item.measure_value)
                        }
                        results.append(result)
        print len(results)
        context = {
            "resutls" : results
        }
        return Response(context)

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
