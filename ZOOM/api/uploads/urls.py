from django.conf.urls import url, include
from api.uploads.views import FilesCreateList
# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register('files', FilesCreateList, 'files')
urlpatterns = [
        # url(r'^$', FilesCreateList.as_view(), name='files-list'),
        # url(r'^$', include(router.urls)),
]

