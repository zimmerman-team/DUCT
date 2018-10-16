from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api.manual_mapper.views import ManualMappingJobResult, ManualMappingJob, ManualMapping, get_data

app_name = 'manaual_map'

urlpatterns = [
    url(r'^$', ManualMappingJob.as_view(), name='manual-mapper'),
    url(r'^manual_map/$', ManualMapping, name='manual-map'),
    url(r'^status$', ManualMappingJobResult.as_view(), name='manual-mapper-result'),
    url(r'^get_data$', get_data, name='manual-mapper-result'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
