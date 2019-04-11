from django.db.models import signals
from django.dispatch import receiver

from mapping.mapper import begin_mapping
from mapping.models import Mapping
from metadata.models import File
from mapping.utils import update_country_on_indicator


@receiver(signals.post_save, sender=Mapping)
def mapping_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        result = begin_mapping(instance.data)

        # if mapping succes then continue to update relation country
        # on the current indicator
        if result.get('success'):
            file_id = instance.data.get('metadata_id')

            try:
                # Updated the country on indicator
                file = File.objects.get(id=file_id)
                update_country_on_indicator(file=file)

            except File.DoesNotExist:
                raise Exception("File does not exists!")
