from django.conf.urls import url
from api.scatter.views import ScatterDataList


urlpatterns = [
    url(r'^$',
        ScatterDataList.as_view(),
        name='scatter-list'),
    ]