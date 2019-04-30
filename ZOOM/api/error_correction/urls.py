from django.conf.urls import url
from api.error_correction.views import error_correction_view

app_name='error_correction'

urlpatterns = [
    url(r'^$', error_correction_view, name='error-correction'),
]
