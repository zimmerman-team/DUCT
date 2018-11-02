from django.db import models
from django.contrib.postgres.fields import JSONField

from metadata.models import File


class Mapping(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    data = JSONField()
