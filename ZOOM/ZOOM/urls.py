from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from graphene_django.views import GraphQLView

from gql.views import AuthenticatedGraphQLView
from gql.public.schema import schema

admin.autodiscover()

app_name = 'main'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^graphql', AuthenticatedGraphQLView.as_view(graphiql=True)),
    url(r'^admin-graphql', staff_member_required(
        GraphQLView.as_view(graphiql=True)
    )),
    url(r'^public-graphql', GraphQLView.as_view(graphiql=True, schema=schema)),
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
