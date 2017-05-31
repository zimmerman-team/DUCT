from django.conf import settings
from django.conf.urls import url

from django.views.decorators.cache import cache_page

from api.indicator.views import IndicatorList
from api.indicator.views import IndicatorDataList
from api.indicator.views import IndicatorDataAggregations
from api.indicator.views import IndicatorCategoryDataList
from api.indicator.views import reset_mapping


urlpatterns = [
    url(r'^$',
        IndicatorDataList.as_view(),
        name='indicator-data-list'),
    url(r'^$',
        IndicatorList.as_view(),
        name='indicator-list'),
    url(r'^list/$',
        IndicatorCategoryDataList.as_view(),
        name='indicator_category-list'),
    url(r'^reset_mapping/$', reset_mapping, name='reset_mapping'),
    url(r'^aggregations/$',
        cache_page(settings.API_CACHE_SECONDS)(IndicatorDataAggregations.as_view()),
        name='indicator-aggregations'),
]
