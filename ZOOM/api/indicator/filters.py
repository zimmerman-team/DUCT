from django_filters import Filter, FilterSet
from api.generics.filters import CommaSeparatedCharFilter
from indicator.models import Indicator, IndicatorDatapoint, IndicatorCategory

from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import CommaSeparatedStickyCharFilter
from rest_framework import filters


class IndicatorDataFilter(FilterSet):

    indicator_category__name = CommaSeparatedStickyCharFilter(
        name='indicator_category__name',
        lookup_expr='in')

    file__authorised = CommaSeparatedStickyCharFilter(
        name='file__authorised',
        lookup_expr='in')

    class Meta:
        model = IndicatorDatapoint
        fields = (
            'id',
            'file',
            'file__authorised',
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


class IndicatorFilter(FilterSet):

    class Meta:
        model = Indicator
        fields = (
            'id',
            'description',
        )

class IndicatorCategoryDataFilter(FilterSet):

    indicator_category__name = CommaSeparatedStickyCharFilter(
        name='indicator_category__name',
        lookup_expr='in')

    #child  = CommaSeparatedStickyCharFilter(
    #    name='child__id',
    #    lookup_expr='in')

    #excluded child below
    class Meta:
        model = IndicatorCategory
        fields = (
            'id',
            'unique_identifier',
            'name',
            'level',
            'parent',
            'indicator',
        )
