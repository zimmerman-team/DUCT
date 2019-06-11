from django.conf.urls import url
from api.metadata.views import FileUploadView

app_name = 'metadata'
urlpatterns = [
    url(r'^upload/$', FileUploadView.as_view(), name='file-upload'),
]
