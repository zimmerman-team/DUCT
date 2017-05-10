from django.conf.urls import url
from . import views
from api.file.views import FileListView, FileDetailView, FileSourceListView, FileTagListView


urlpatterns = [
        url(r'^update_status/$', views.update_status, name='update_status'),
        url(r'^$', FileListView.as_view(), name='file-list'),
        url(r'^sources/$', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^(?P<pk>[^@$&+,/:;=?]+)/', FileDetailView.as_view(), name='file-detail'),
        url(r'^(?P<pk>\d+)/tags/$', FileTagListView.as_view(), name='file-tag-list'),

]


# url(r'^(?P<pk>[^@$&+,/:;=?]+)/',
#         api.chain.views.ChainDetail.as_view(),
#         name='chain-detail'),
#     ]