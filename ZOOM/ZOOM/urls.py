from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from api.views import overview
import debug_toolbar

from graphene_django.views import GraphQLView

admin.autodiscover()

app_name='main'

urlpatterns = [
    url(r'^$', overview, name='api-root'),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^graphql', GraphQLView.as_view(graphiql=True)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
