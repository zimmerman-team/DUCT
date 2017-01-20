from django.db import models
import uuid
from django.core.urlresolvers import reverse
import os
from django.conf import settings
import requests
from django.core.files.base import ContentFile
import rfc6266  # (content-disposition header parser)
from django.conf import settings
from django.utils import timezone
import datetime

CONTENT_TYPE_MAP = {
    'application/json': 'json',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'text/csv': 'csv'
}


def upload_to(instance, filename=''):
	#create datasets if it doesnt exist
        #return os.path.join(str(instance.pk), filename)
    return os.path.join(settings.MEDIA_ROOT + "/datasets/", filename)

#Basic data store for the test file being used
class Store(models.Model):
    file_source = models.CharField(max_length = 50)
    date_created =  models.DateTimeField(default=timezone.now)
    indicator_type = models.CharField(max_length=50)
    indicator = models.CharField(max_length=40)
    unit = models.CharField(max_length=50)
    subgroup = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    country_id = models.CharField(max_length=5)
    date = models.DateField(("Date")) # identify timezone?
    source = models.CharField(max_length=5)
    value = models.DecimalField(max_digits=20, decimal_places = 5) # might need more for accuracy
    footnote = models.CharField(max_length=200)

#the mapping betweeen coulmns in the datastore and HXL tags
class HXLmapping(models.Model): #can be used for other conversions
    column_name = models.CharField(max_length = 50)
    HXL_tag = models.CharField(max_length = 50) #HXL tags can error tags

#HXL and the corresponding value type for that tag
class HXLtags(models.Model):
    HXL_tag = models.CharField(max_length = 50)
    value_type = models.CharField(max_length = 40)

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_url = models.URLField(null=True, max_length=2000)
    file = models.FileField(upload_to=upload_to)
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