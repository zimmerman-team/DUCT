from django.conf.urls import url
from django.conf.urls import include
from api import views

urlpatterns = [
    url(r'^$', views.welcome, name='api-root'),
    url(r'^indicators/', include('api.indicator.urls', namespace='indicators')),
    url(r'^uploads/', include('api.uploads.urls', namespace='uploads')),
    url(r'^scatter/', include('api.scatter.urls', namespace='scatter')),
    url(r'^file/', include('api.file.urls')),
    url(r'^validate/', include('api.validate.urls')),
    ]

