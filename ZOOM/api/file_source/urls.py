from django.conf.urls import url
from api.file_source.views import FileSourceListView, FileSourceDetailView, TagsListView


urlpatterns = [
        url(r'^$', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^(?P<pk>\d+)/$', FileSourceDetailView.as_view(), name='file-source-detail'),
        url(r'^(?P<file_source_pk>\d+)/tags/$', TagsListView.as_view(), name='file-tags-list'),
        # url(r'^(?P<pk>\d+)/tags/(?P<file_source_pk>\d+)/$', TagsListView.as_view(), name='file-tags-list'),
]
