from django.conf.urls import url

from api.file.views import FileListView, FileDetailView, FileSourceListView, FileTagListView


urlpatterns = [
        url(r'^$', FileListView.as_view(), name='file-list'),
        url(r'^(?P<pk>\d+)/$', FileDetailView.as_view(), name='file-detail'),
        url(r'^sources/', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^(?P<pk>\d+)/tags/$', FileTagListView.as_view(), name='file-tag-list')
]
