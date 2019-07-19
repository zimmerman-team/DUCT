from django.conf.urls import url
from api.generics.views import remove_geo_json

app_name = 'generic'
urlpatterns = [
    url(r'^removeGeo/$', remove_geo_json, name='remove-geo'),
]
