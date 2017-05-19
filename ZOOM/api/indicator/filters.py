
from django_filters import Filter, FilterSet
from api.generics.filters import CommaSeparatedCharFilter
from indicator.models import IndicatorDatapoint, IndicatorCategory

class IndicatorDataFilter(FilterSet):

    class Meta:
        model = IndicatorDatapoint
        fields = (
            'id',
            'file',
            'date_format',
            'indicator_category',
            'indicator',
            'country',
            'date_value',
            'source',
            'country__region',
            'country__name',
            'unit_of_measure',
        )

class IndicatorCategoryDataFilter(FilterSet):

    class Meta:
        model = IndicatorCategory
        fields = (
            'id',
            'name',
            'level',
            'child',
            'indicator',
        )
