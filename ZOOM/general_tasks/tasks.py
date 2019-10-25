import os

from celery import task
from django.conf import settings

from metadata.models import File


@task
def clean_temp_geo_jsons():
    path_to_temp = os.path.join(settings.BASE_DIR, 'static/temp_geo_jsons/')
    list_of_files = os.listdir(path_to_temp)
    for file in list_of_files:
        if file.startswith('geo_json'):
            full_path = os.path.join(path_to_temp, file)
            os.remove(full_path)


# @task
# def delete_garbage_uploaded_files():
#     """
#     This task to remove all files which have not related to File model.
#     :return:
#     """
#     dataset_root = settings.MEDIA_ROOT + '/datasets/'
#
#     for file in os.listdir(dataset_root):
#         filename = os.fsdecode(file)
#         full_path_filename = os.path.join(dataset_root, filename)
#
#         # '.new.csv' is default DUCT extension file
#         if filename[-8:] != '.new.csv':
#             os.remove(full_path_filename)
#         else:
#             files = File.objects.filter(file=full_path_filename)
#
#             # if not related to File model then delete it
#             if not files:
#                 os.remove(full_path_filename)
