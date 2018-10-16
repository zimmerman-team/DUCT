from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
import debug_toolbar

from graphene_django.views import GraphQLView

admin.autodiscover()

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/queue/', include('django_rq.urls')),
    url(r'^admin/task_queue/', include('task_queue.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^graphql', GraphQLView.as_view(graphiql=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
