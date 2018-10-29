from django.conf.urls import url
from django.conf.urls import include
from api.views import welcome 

app_name='api'

urlpatterns = [
    url(r'^$', welcome, name='api-root'),
    url(r'^metadata/', include('api.metadata.urls', namespace='metadata')),
    url(r'^indicators/', include('api.indicator.urls', namespace='indicators')),
    url(r'^validate/', include('api.validate.urls', namespace='validate')),
    url(r'^mapping/', include('api.mapping.urls', namespace='=mapping')),
    #url(r'^error-correction/', include('api.error_correction.urls', namespace='error-correction'))
]
