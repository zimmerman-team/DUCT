from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
#from api.validate.views import Validation

urlpatterns = [
    url(r'^$', views.Validate.as_view(), name='validate'),
    url(r'^check_file_valid/$', views.check_file_valid, name='check_file_valid'),
    #url(r'^$', Validation.as_view()),
    #url(r'^(?P<pk>[0-9]+)/$', FileDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)