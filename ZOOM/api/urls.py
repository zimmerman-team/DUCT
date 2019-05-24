from django.conf.urls import url
from django.conf.urls import include
from api.views import welcome 

app_name='api'

urlpatterns = [
    url(r'^$', welcome, name='api-root'),
    url(r'^metadata/', include('api.metadata.urls', namespace='metadata')),
]
