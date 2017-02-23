from rest_framework.filters import DjangoFilterBackend

from api.generics.views import DynamicListView

from api.indicator.serializers import *

from indicator.models import IndicatorDatapoint


class IndicatorDataList(DynamicListView):


    queryset = IndicatorDatapoint.objects.all()
    filter_backends = (DjangoFilterBackend, )
    # filter_class = IndicatorDataFilter
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