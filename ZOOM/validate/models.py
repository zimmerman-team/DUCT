import uuid
import os
import requests
import rfc6266
import datetime

from django.db import models
from django.core.urlresolvers import reverse
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
	#create datasets if it doesnt exist
    #return os.path.join(str(instance.pk), filename)
    return os.path.join(settings.MEDIA_ROOT + "/datasets/", filename)


# Temp storage of file. Used until mapping is complete
class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_url = models.URLField(null=True, max_length=2000)
    file = models.FileField(upload_to=upload_to)
    file_name = models.CharField(max_length = 200, default="default")
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    rendered = models.BooleanField(default=False)

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

    def get_absolute_url(self):
        return reverse('zoom_demo:explore', args=(self.pk,), current_app=self.current_app)

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
                r = requests.get(self.source_url, headers={'User-Agent': 'Cove (cove.opendataservice.coop)'})
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

