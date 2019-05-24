# Create your tasks here
from __future__ import absolute_import, unicode_literals
import time
from celery import shared_task
from celery.result import AsyncResult

# import the logging library
import logging

from mapping.mapper import begin_mapping
from metadata.models import File
from mapping.utils import update_country_on_indicator
from mapping.models import Mapping

# Get an instance of a logger
logger = logging.getLogger(__name__)


def mapping(instance):
    file_id = instance.data.get('metadata_id')
    try:
        file = File.objects.get(id=file_id)

        # When mapping again will be deleted all old indicator related
        # to the current file
        file.indicator_set.all().delete()

    except File.DoesNotExist:
        raise Exception(
            'File {file_id} does not exists!'.format(file_id=file_id)
        )

    try:
        # Begin mapping
        result = begin_mapping(instance.data)

        # if mapping success then continue to update relation country
        # on the current indicator
        if result.get('success'):
            update_country_on_indicator(file=file)

    except Exception as e:
        raise Exception(e)


@shared_task
def mapping_task(mapping_id):
    instance = Mapping.objects.get(id=mapping_id)

    try:
        mapping(instance)
    except Exception as e:
        # Save error to the mapping model
        instance.error_message = 'Failed: {e}'.format(e=str(e))
        instance.save()

        # Send error to logger
        logger.exception(msg=str(e))

        # Send exception to Celery
        raise Exception(e)


@shared_task
def mapping_status_task(mapping_id, task_id):
    instance = Mapping.objects.get(id=mapping_id)
    instance.task_id = task_id

    while instance.status in ['INITIAL', 'PENDING', 'STARTED']:
        instance.status = AsyncResult(task_id).status
        instance.save()

        # Sleep every 1 minutes
        time.sleep(60)
