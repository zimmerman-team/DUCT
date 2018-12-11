from django.conf.urls import url
from api.error_correction.views import ErrorCorrectionView

app_name='error_correction'

urlpatterns = [
    url(r'^$', ErrorCorrectionView, name='error-correction'),
]
