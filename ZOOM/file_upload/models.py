import uuid
import os
import requests
import rfc6266
import datetime

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone


CONTENT_TYPE_MAP = {
    'application/json': 'json',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'text/csv': 'csv'
}


def upload_to(instance, filename=''):
    return os.path.join(settings.MEDIA_ROOT + "/datasets/", filename)


class FileTag(models.Model):
    name = models.CharField(max_length=50)


class FileSource(models.Model):
    name = models.CharField(max_length=100)

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=False)
    tags = models.ManyToManyField(FileTag)
    data_source = models.ForeignKey(FileSource, null=True, on_delete=models.SET_NULL)
    in_progress = models.BooleanField(default=False)
    source_url = models.URLField(null=True, max_length=2000)
    file = models.FileField(upload_to=upload_to)
    file_name = models.CharField(max_length = 200, default="default")
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    rendered = models.BooleanField(default=False)
    status = models.IntegerField(default=1)
    authorised = models.BooleanField(default=False)
    mapping_used = models.CharField(max_length=1000, null=True, blank=True)

    form_name = models.CharField(
        max_length=20,
        choices=[
            ('upload_form', 'File upload'),
            ('url_form', 'Downloaded from URL'),
            ('text_form', 'Pasted into textarea'),
        ],
        null=True
    )

    def filename(self):
        return os.path.basename(self.file.name)

    def update_filename(self, updated_name):
        self.file.name = updated_name
        self.save()

    def get_file_path(self):
        return settings.MEDIA_ROOT + "/datasets/" + os.path.basename(self.file.name)
        #return os.path.join(str(instance.pk), filename)

    def upload_dir(self):#change to upload to different places 
        return os.path.join(settings.MEDIA_ROOT, upload_to(self))
    
    def upload_url(self):
        return os.path.join(settings.MEDIA_URL, upload_to(self))

    def is_google_doc(self):
        return self.source_url.startswith('https://docs.google.com/')

    def download(self):
        if self.source_url:
            if self.is_google_doc():
                get_google_doc(self)
            else:
                r = requests.get(self.source_url, headers={'User-Agent': 'ZOOM (zoom.aidsfonds.nl)'})
                r.raise_for_status()
                content_type = r.headers.get('content-type', '').split(';')[0].lower()
                file_extension = CONTENT_TYPE_MAP.get(content_type)

                if not file_extension:
                    possible_extension = rfc6266.parse_requests_response(r).filename_unsafe.split('.')[-1]
                    if possible_extension in CONTENT_TYPE_MAP.values():
                        file_extension = possible_extension

                file_name = r.url.split('/')[-1].split('?')[0][:100]
                if file_name == '':
                    file_name = 'file'
                if file_extension:
                    if not file_name.endswith(file_extension):
                        file_name = file_name + '.' + file_extension
                self.original_file.save(
                    file_name,
                    ContentFile(r.content))
        else:
            raise ValueError('No source_url specified.')

class FileDtypes(models.Model):
    dtype_name = models.CharField(max_length=500, null=True)#location  
    dtype_dict_name = models.CharField(max_length=500, null=True)#location    
    file = models.OneToOneField("File", null=True)
    #include method that deletes physical file if row deleted


def check_files():
    """Deletes files not saved in data model."""

    file_objects = File.objects.all()
    found_files = []
    found_tmpfiles = []

    for file_ob in file_objects:
        found_files.append(str(file_ob.file))
        found_tmpfiles.append(str(FileDtypes.objects.get(file=file_ob).dtype_name))
        found_tmpfiles.append(str(FileDtypes.objects.get(file=file_ob).dtype_dict_name))

    found_files = set(found_files)
    found_tmpfiles = set(found_tmpfiles)
    datasets_path = str(os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/datasets'))
    tmp_path = str(os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/tmpfiles'))
    tmp_dir = (os.listdir(tmp_path))
    datasets_dir = (os.listdir(datasets_path))
    datasets_dir = set([str(datasets_path + "/" + s) for s in datasets_dir])
    tmp_dir = set([str(tmp_path + "/" + s) for s in tmp_dir])
    
    diff_files, diff_tmpfiles = datasets_dir.difference(found_files), tmp_dir.difference(found_tmpfiles)
    file_sets = [diff_files, diff_tmpfiles]
    
    print("size datasets", len(datasets_dir))
    print("size diff", len(diff_files))
    count = 0
    
    for i in range(len(file_sets)):
        if len(file_sets[i]) > 0:
            for j in file_sets[i]:
                os.remove(j)
                count = count + 1
                
    print("Removed files: ", count, "!")
    #Cycle through files
    #get all files, validation results and tmp_files

    #get all files in directories
    #get boolean list of files existing
    #remove files flagged as false from directories 