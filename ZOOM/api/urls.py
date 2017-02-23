from django.conf.urls import url
from django.conf.urls import include
from api import views

urlpatterns = [
    url(r'^$', views.welcome, name='api-root'),
    url(r'^indicators/', include('api.indicator.urls', namespace='indicators')),
    url(r'^scatter/', include('api.scatter.urls', namespace='scatter')),
    ]

