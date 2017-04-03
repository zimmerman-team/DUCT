from django.conf.urls import url
from api.uploads.views import UploadsCreateList, MapperView


urlpatterns = [
        url(r'^$', UploadsCreateList.as_view(), name='uploads-list'),
        url(r'^mapper/$', MapperView.as_view(), name='mapper-list'),
]

