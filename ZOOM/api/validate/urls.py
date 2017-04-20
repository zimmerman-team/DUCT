from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^$', views.Validate.as_view(), name='validate'),
    url(r'^check_file_valid/$', views.check_file_valid, name='check_file_valid'),
]

urlpatterns = format_suffix_patterns(urlpatterns)