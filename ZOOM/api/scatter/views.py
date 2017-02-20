from rest_framework.filters import DjangoFilterBackend

from api.generics.views import DynamicListView

from api.scatter.serializers import *

from indicator.models import ScatterData


class ScatterDataList(DynamicListView):


    queryset = ScatterData.objects.all()
    filter_backends = (DjangoFilterBackend, )
    # filter_class = IndicatorDataFilter
    serializer_class = ScatterSerializer

    fields = (
        'id',
        'Category',
        'Indicator_1',
        'Indicator_1_value',
        'Indicator_2',
        'Indicator_2_value',
        'Country',
        )