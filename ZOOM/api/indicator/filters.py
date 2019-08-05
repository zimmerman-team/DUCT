import urllib

from django_filters import FilterSet
from rest_framework import filters

from api.generics.filters import CommaSeparatedStickyCharFilter
from indicator.models import \
    Indicator  # , IndicatorDatapoint, IndicatorCategory


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

#check if this can be removed
'''class ListFilter(Filter):
    def filter(self, qs, value):
        ids = IndicatorFilter.objects.filter(name=value).values_list('id', flat=True)
        #value_list = value.split(u',')
        return IndicatorDatapoint.objects.filter(pk__in=ids) #super(ListFilter, self).filter(qs, lookup(value_list, 'in'))

class IndicatorListFilter(Filter):
    def filter(self, qs, value):
        print("qs ", qs)
        print("value ", value)
        ind = Indicator.objects.get(id=urllib.unquote(value))
        print("ids ", ind)
        #print(qs.filter(indicator=ind).count())
        #value_list = value.split(u',')
        return qs.filter(indicator=ind) #super(ListFilter, self).filter(qs, lookup(value_list, 'in'))

#need to change this filter set!!!
class IndicatorDataFilter(FilterSet):

    file__authorised = BooleanFilter(name='file__authorised')
    id = ListFilter(name='id')
    indicator = CharFilter(method='ind_filter')

    file__source = CommaSeparatedStickyCharFilter(
        name='file__data_source__name',
        lookup_expr='in')
    #serializer_class = Indicator

    class Meta:
        model = Datapoints
        fields = (
            'id',
            'file',
            'file__authorised',
            'file__source',
            'date_format',
            #'indicator_category',
            #'indicator_category__name',
            'indicator',
            'country',
            'date_value',
            'source',
            'country__region',
            'country__name',
            'measure_value',
            'unit_of_measure'
        )
'''

'''    
    def ind_filter(self, qs, name, value):
        ind = Indicator.objects.get(id=urllib.unquote(value))
        #print(qs.filter(indicator=ind).count())
        #value_list = value.split(u',')
        return qs.filter(indicator=ind) #super(ListFilter, self).filter(qs, lookup(value_list, 'in'))

class IndicatorFilterHeadingFilter(FilterSet):
    file_source = CommaSeparatedStickyCharFilter(
        name='file_source__name',
        lookup_expr='in')

    class Meta:
        model = IndicatorFilterHeading
        fields = (
            'name',
            'file_source'
        )

class IndicatorFilterFilters(FilterSet):
    file_source = CommaSeparatedStickyCharFilter(
        name='file_source__name',
        lookup_expr='in')

    class Meta:
        model = IndicatorFilter
        fields = (
            'name',
            'heading',
            'measure_value',
            'file_source'
        )

class IndicatorFilters(FilterSet):

    #file__authorised = BooleanFilter(name='indicatordatapoint__file__authorised')
    
    file_source__name = CommaSeparatedStickyCharFilter(
        name='file_source__name',
        lookup_expr='in')

    class Meta:
        model = Indicator
        fields = (
            'indicator_id',
            'description',
            'file_source'
        )

'''
'''class IndicatorCategoryDataFilter(FilterSet):
            'count',
            'file_source',
            'file_source__name'
        )

'''
