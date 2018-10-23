from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tags/(?P<id>[0-9]+)/', views.tags, name='tags'),
]
