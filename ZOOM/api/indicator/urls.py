from django.conf.urls import url
from api.indicator.views import IndicatorDataList
# from api.indicator.views import IndicatorAggregations


urlpatterns = [
    url(r'^$',
        IndicatorDataList.as_view(),
        name='indicator-list'),
    ]