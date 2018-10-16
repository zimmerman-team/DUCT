from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from api.views import overview
import debug_toolbar


admin.autodiscover()

app_name='main'

urlpatterns = [
    url(r'^$', overview, name='api-root'),
    #url(r'^grappelli/', include('grappelli.urls', namespace='grappelli')),
    #url(r'^admin/queue/', include('django_rq.urls', namespace='django_rq')),
    #url(r'^admin/task_queue/', include('task_queue.urls', namespace='task_queue')),
    #url(r'^admin/', include(admin.site.urls, namespace='admin')),
    url(r'^api/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
