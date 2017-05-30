from django.conf.urls import url
from api.indicator.views import IndicatorDataList, IndicatorDataAggregations, IndicatorCategoryDataList
from . import views

from django.views.decorators.cache import cache_page
from django.conf import settings


urlpatterns = [
    url(r'^$',
        IndicatorDataList.as_view(),
        name='indicator-list'),
    url(r'^category/$',
        IndicatorCategoryDataList.as_view(),
        name='indicator_category-list'),
    url(r'^reset_mapping/$', views.reset_mapping, name='reset_mapping'),
    url(r'^aggregations/$',
        cache_page(settings.API_CACHE_SECONDS)(IndicatorDataAggregations.as_view()),
        name='indicator-aggregations'),
]
