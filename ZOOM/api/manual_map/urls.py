from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^manual_map/$', views.manual_mapping, name='manual_map'),
]

urlpatterns = format_suffix_patterns(urlpatterns)