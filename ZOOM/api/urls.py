from django.conf.urls import url
from django.conf.urls import include

from api.views import welcome 


urlpatterns = [
    url(r'^$', welcome, name='api-root'),
    url(r'^indicators/', include('api.indicator.urls', namespace='indicators')),
    url(r'^file/', include('api.file.urls', namespace='file')),
    url(r'^validate/', include('api.validate.urls', namespace='validate')),
    url(r'^manual-mapper/', include('api.manual_mapper.urls', namespace='manual-mapper')),
    url(r'^error-correction/', include('api.error_correction.urls', namespace='error-correction'))
]
