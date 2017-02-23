from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^selector/', views.data_selector, name='data_selector'),
    url(r'^scatter_api/', views.scatter_api, name='scatter_api'),
    

]