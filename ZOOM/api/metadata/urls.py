from django.conf.urls import url
from . import views
from api.metadata.views import FileListView, FileDetailView, FileSourceListView

app_name = 'metadata'

urlpatterns = [
        url(r'^$', FileListView.as_view(), name='file-list'),
        url(r'^add_remove_source/$', views.add_remove_source, name='add_remove_source'),
        url(r'^sources/$', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^(?P<pk>[^@$&+,/:;=?]+)/', FileDetailView.as_view(), name='file-detail'),
]
