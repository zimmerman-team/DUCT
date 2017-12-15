from django_filters import Filter, FilterSet
from api.generics.filters import CommaSeparatedCharFilter
from indicator.models import Indicator, IndicatorDatapoint, IndicatorCategory

from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import CommaSeparatedStickyCharFilter
from django_filters import BooleanFilter
from rest_framework import filters


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        query = request.query_params.get('q', None)
        query_lookup = request.query_params.get('q_lookup', None)
        lookup_expr = 'exact' #'ft'
        if query_lookup:
            lookup_expr = query_lookup

        if query:
            return queryset.filter(**{'search_vector_text__{0}'.format(lookup_expr): query})

        return queryset


class IndicatorDataFilter(FilterSet):

    indicator_category__name = CommaSeparatedStickyCharFilter(
        name='indicator_category__name',
        lookup_expr='in')

    file__authorised = BooleanFilter(name='file__authorised')

    file__source = CommaSeparatedStickyCharFilter(
        name='file__data_source__name',
        lookup_expr='in')

    class Meta:
        model = IndicatorDatapoint
        fields = (
            'id',
            'file',
            'file__authorised',
            'file__source',
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
            'unit_of_measure'
        )


class IndicatorFilter(FilterSet):

    file__authorised = BooleanFilter(name='indicatordatapoint__file__authorised')
    
    file_source__name = CommaSeparatedStickyCharFilter(
        name='file_source__name',
        lookup_expr='in')

    class Meta:
        model = Indicator
        fields = (
            'id',
            'description',
            'count',
            'file_source'
        )


class IndicatorCategoryDataFilter(FilterSet):

    file__authorised = BooleanFilter(name='indicator__indicatordatapoint__file__authorised')

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
