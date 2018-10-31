from django.db import models
from django.contrib.postgres.fields import JSONField

from metadata.models import FileSource


class Mapping(models.Model):
    file_source = models.ForeignKey(FileSource, on_delete=models.CASCADE)
    data = JSONField()