from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api.mapping.views import MappingJobResult, MappingJob, get_data

app_name = 'mapping'

urlpatterns = [
    url(r'^$', MappingJob.as_view(), name='mapping'),
    url(r'^status$', MappingJobResult.as_view(), name='manual-mapper-result'),
    url(r'^get_data$', get_data, name='manual-mapper-result'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
