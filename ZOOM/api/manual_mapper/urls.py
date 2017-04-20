from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns

from api.manual_mapper.views import ManualMappingJobResult, ManualMappingJob, ManualMapping


urlpatterns = [
    url(r'^$', ManualMappingJob.as_view(), name='manual-mapper'),
    url(r'^manual_map$', ManualMapping, name='manual-map'),
    url(r'^status$', ManualMappingJobResult.as_view(), name='manual-mapper-result'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
