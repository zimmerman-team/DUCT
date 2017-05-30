
from django_filters import Filter, FilterSet
from api.generics.filters import CommaSeparatedCharFilter
from indicator.models import IndicatorDatapoint, IndicatorCategory


from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import CommaSeparatedStickyCharFilter
from rest_framework import filters



class IndicatorDataFilter(FilterSet):

    indicator_category__name = CommaSeparatedStickyCharFilter(
        name='indicator_category__name',
        lookup_expr='in')

    class Meta:
        model = IndicatorDatapoint
        fields = (
            'id',
            'file',
            'date_format',
            'indicator_category',
            'indicator_category__name',
            'indicator',
            'country',
            'date_value',
            'source',
            'country__region',
            'country__name',
            'measure_value',
            'unit_of_measure',
        )

class IndicatorCategoryDataFilter(FilterSet):

    class Meta:
        model = IndicatorCategory
        fields = (
            'id',
            'unique_identifier',
            'name',
            'level',
            'child',
            'indicator',
        )
