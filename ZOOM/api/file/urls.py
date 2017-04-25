from django.conf.urls import url

from api.file.views import FileListView, FileDetailView, FileSourceListView, FileTagListView, delete_file


urlpatterns = [
        url(r'^delete_file/$', delete_file, name='delete_file'),
        url(r'^$', FileListView.as_view(), name='file-list'),
        url(r'^(?P<pk>[^@$&+,/:;=?]+)/', FileDetailView.as_view(), name='file-detail'),
        url(r'^sources/', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^(?P<pk>\d+)/tags/$', FileTagListView.as_view(), name='file-tag-list')
]


# url(r'^(?P<pk>[^@$&+,/:;=?]+)/',
#         api.chain.views.ChainDetail.as_view(),
#         name='chain-detail'),
#     ]