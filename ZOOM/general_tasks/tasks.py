from celery import task
from django.conf import settings
import os

@task
def clean_temp_geo_jsons():
    path_to_temp = os.path.join(settings.BASE_DIR, 'static/temp_geo_jsons/')
    list_of_files = os.listdir(path_to_temp)
    for file in list_of_files:
        if file.startswith('geo_json'):
            full_path = os.path.join(path_to_temp, file)
            os.remove(full_path)
