from django.db.models import signals
from django.dispatch import receiver

from metadata.models import File
from validate.validator import validate


@receiver(signals.post_save, sender=File)
def file_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        validate(instance.id)
