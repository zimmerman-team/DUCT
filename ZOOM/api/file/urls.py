from django.conf.urls import url

from api.file.views import FileListView, FileDetailView, FileSourceListView, FileTagListView, FileView


urlpatterns = [
        url(r'^$', FileView.as_view(), name='file'),
        url(r'^file-list/$', FileListView.as_view(), name='file-list'),
        url(r'^file-list/(?P<pk>[0-9a-f-]+)/$', FileDetailView.as_view(), name='file-detail'),
        url(r'^sources/', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^tags/$', FileTagListView.as_view(), name='file-tag-list')
]
