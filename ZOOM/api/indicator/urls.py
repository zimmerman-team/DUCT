from django.conf import settings
from django.conf.urls import url

from django.views.decorators.cache import cache_page

#from api.indicator.views import IndicatorList
#from api.indicator.views import IndicatorDataList
#from api.indicator.views import IndicatorDataAggregations
#from api.indicator.views import IndicatorCategoryDataList
#from api.indicator.views import reset_mapping


#app_name = 'indicator'

#urlpatterns = [
#    url(r'^indicator/',
#        IndicatorList.as_view(),
#        name='indicator'),]
''' url(r'^data/$',
        IndicatorDataList.as_view(),
        name='indicator-data-list'),
    url(r'^filters/aggregations/$', show_unique_filters, name='filter-aggregations'),
    url(r'^filters/$',
        IndicatorFilterList.as_view(),
        name='indicator_category-list'),
    url(r'^reset_mapping/$', reset_mapping, name='reset_mapping'),
    url(r'^get_filter_headings/$', IndicatorFilterHeadingList.as_view(), name='get_filter_headings'),
    url(r'^aggregations/$',
        cache_page(settings.API_CACHE_SECONDS)(IndicatorDataAggregations.as_view()),
        name='indicator-aggregations'),'''
#]
