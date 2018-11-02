from django.db.models import signals
from django.dispatch import receiver

from validate.validator import validate
from mapping.models import Mapping


@receiver(signals.post_save, sender=Mapping)
def file_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        validate(instance.id)
