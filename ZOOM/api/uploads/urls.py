from django.conf.urls import url
from api.uploads.views import UploadsCreateList, MapperView, ManualMappingJob, ManualMappingJobResult


urlpatterns = [
        url(r'^$', UploadsCreateList.as_view(), name='uploads-list'),
        url(r'^mapper/$', MapperView.as_view(), name='mapper-list'),
        url(r'^manual-mapper/$', ManualMappingJob.as_view(), name='manual-mapper'),
        url(r'^manual-mapper-result/$', ManualMappingJobResult.as_view(), name='manual-mapper-result'),
]

