from django.conf.urls import url
from api.error_correction.views import ErrorCorrectionView


urlpatterns = [
    url(r'^$', ErrorCorrectionView, name='error-correction'),
]
