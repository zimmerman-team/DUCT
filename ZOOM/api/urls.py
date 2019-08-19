from django.conf.urls import include, url

from api.views import welcome

app_name = 'api'

urlpatterns = [
    url(r'^$', welcome, name='api-root'),
    url(r'^metadata/', include('api.metadata.urls', namespace='metadata')),
    url(r'^generic/', include('api.generics.urls', namespace='generic')),
]
