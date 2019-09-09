from django.db.models import signals
from django.dispatch import receiver

from mapping.models import Mapping
from mapping.tasks import mapping_status_task, mapping_task


@receiver(signals.post_save, sender=Mapping)
def mapping_post_save(sender, instance, **kwargs):
    if instance.status == 'INITIAL':
        mapping_id = instance.id

        # Run mapping
        task = mapping_task.delay(mapping_id=mapping_id)

        # Update mapping status periodically
        mapping_status_task.delay(
            mapping_id=mapping_id,
            task_id=task.id
        )
