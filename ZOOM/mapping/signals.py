from django.db.models import signals
from django.dispatch import receiver

from mapping.mapper import begin_mapping
from mapping.models import Mapping

@receiver(signals.post_save, sender=Mapping)
def file_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        begin_mapping(instance)
