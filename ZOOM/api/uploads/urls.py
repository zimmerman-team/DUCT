from django.conf.urls import url
from api.uploads.views import UploadsCreateList, MapperView
from api.manual_mapper.views import ManualMappingJobResult


urlpatterns = [
        url(r'^$', UploadsCreateList.as_view(), name='uploads-list'),
        url(r'^mapper/$', MapperView.as_view(), name='mapper-list'),
        url(r'^manual-mapper/status$', ManualMappingJobResult.as_view(), name='manual-mapper-result'),
]
