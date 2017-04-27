from django.conf.urls import url

from api.file.views import FileListView, FileDetailView, FileSourceListView, FileTagListView, FileView


urlpatterns = [
<<<<<<< HEAD
        url(r'^$', FileView.as_view(), name='file'),
        url(r'^file-list/$', FileListView.as_view(), name='file-list'),
        url(r'^file-list/(?P<pk>[0-9a-f-]+)/$', FileDetailView.as_view(), name='file-detail'),
=======
        url(r'^$', FileListView.as_view(), name='file-list'),
        url(r'^(?P<pk>[^@$&+,/:;=?]+)/', FileDetailView.as_view(), name='file-detail'),
>>>>>>> upstream/develop
        url(r'^sources/', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^tags/$', FileTagListView.as_view(), name='file-tag-list')
]


# url(r'^(?P<pk>[^@$&+,/:;=?]+)/',
#         api.chain.views.ChainDetail.as_view(),
#         name='chain-detail'),
#     ]