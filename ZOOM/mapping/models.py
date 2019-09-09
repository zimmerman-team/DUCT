from django.contrib.postgres.fields import JSONField
from django.db import models

from metadata.models import File


class Mapping(models.Model):
    STATUS_CHOICES = (
        ('INITIAL', 'INITIAL'),
        ('PENDING', 'PENDING'),
        ('RECEIVED', 'RECEIVED'),
        ('STARTED', 'STARTED'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILURE', 'FAILURE'),
        ('REVOKED', 'REVOKED'),
        ('RETRY', 'RETRY'),
    )
    file = models.OneToOneField(
        File,
        null=True,
        default=None,
        on_delete=models.CASCADE
    )
    data = JSONField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='INITIAL'
    )
    error_message = models.TextField(blank=True, null=True, default='')
    task_id = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        default=''
    )
    session_email = models.EmailField(blank=True, null=True, default=None)

    def __str__(self):
        return str(self.id)
