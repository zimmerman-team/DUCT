from django.conf.urls import url
from api.uploads.views import UploadsCreateList, ErrorCorrectionView
from api.manual_mapper.views import ManualMappingJobResult


urlpatterns = [
        url(r'^$', UploadsCreateList.as_view(), name='uploads-list'),
        url(r'^error-correction/$', ErrorCorrectionView.as_view(), name='error-correction-list'),
        url(r'^manual-mapper/status$', ManualMappingJobResult.as_view(), name='manual-mapper-result'),
]
