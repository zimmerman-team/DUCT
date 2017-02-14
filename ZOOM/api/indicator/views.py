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
        'measure_value',
        #'unique_id',
        # 'full_date',
        # 'name', 
        # 'value',
        )