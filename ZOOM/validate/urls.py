from django.conf.urls import url

from . import views

urlpatterns = [
	
    url(r'^$', views.index, name='index'),
    url(r'^report/$', views.report, name='report'),   
    url(r'^report_update/(?P<file_name>[\w.]{0,256})/$', views.correction_report, name='correction_report'),
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^update_file/(?P<file_name>[\w.]{0,256})/(?P<file_temp>[\w.]{0,256})/$', views.update_file, name='update_file'),
]