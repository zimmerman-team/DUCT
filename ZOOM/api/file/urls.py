from django.conf.urls import url
from . import views
from api.file.views import FileListView, FileDetailView, FileSourceListView

app_name = 'file'

urlpatterns = [
        url(r'^update_status/$', views.update_status, name='update_status'),
        url(r'^add_remove_source/$', views.add_remove_source, name='add_remove_source'),
        url(r'^$', FileListView.as_view(), name='file-list'),
        url(r'^sources/$', FileSourceListView.as_view(), name='file-source-list'),
        url(r'^(?P<pk>[^@$&+,/:;=?]+)/', FileDetailView.as_view(), name='file-detail'),
]
