from django.conf.urls import url
from api.uploads.views import UploadsCreateList


urlpatterns = [
        url(r'^$', UploadsCreateList.as_view(), name='uploads-list'),
]

