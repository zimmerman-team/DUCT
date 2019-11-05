from django.conf.urls import url

from api.generics.views import remove_tiles

app_name = 'generic'
urlpatterns = [
    url(r'^removeTiles/$', remove_tiles, name='remove-tiles'),
]
