from django.conf.urls import url
from api.uploads.views import UploadsCreateList
# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register('files', FilesCreateList, 'files')
urlpatterns = [
        url(r'^$', UploadsCreateList.as_view(), name='uploads-list'),
        # url(r'^$', include(router.urls)),
]

