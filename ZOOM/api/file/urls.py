from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api.file.views import FileList, FileDetail

urlpatterns = [
    url(r'^$', FileList.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', FileDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)