from django.db import models
from django.contrib.postgres.fields import JSONField


class Mapping(models.Model):
    data = JSONField()
