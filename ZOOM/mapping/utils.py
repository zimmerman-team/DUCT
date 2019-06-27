import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from indicator.models import Indicator
from geodata.models import COUNTRY_RELATION_TYPES
from mapping.models import Mapping

import gql.utils


def update_country_on_indicator(file):
    # Get indicator from file source
    indicators = Indicator.objects.filter(file=file)

    for indicator in indicators:
        # Get first data pint to check an geelocation on it
        data_point = indicator.datapoints_set.first()
        if data_point:
            # Check if type of the geolocation is postcode,
            # province, country, etc.
            geolocation = data_point.geolocation

            # All COUNTRY_RELATION_TYPES
            if geolocation.type in COUNTRY_RELATION_TYPES:
                # Save the relation country of the geolocation
                country = geolocation.content_object.country

                if country:
                    indicator.country = country
                    indicator.save()


def send_confirmation_email(status, file_id, mapping_id, error_message=None):

    if status:
        template = render_to_string('mapping/status_success.txt', {
            'file_id': file_id,
            'mapping_id': mapping_id,
        })
        subject = settings.ZOOM_TASK_EMAIL_MAPPING_SUCCESS_SUBJECT
    else:
        template = render_to_string('mapping/status_failed.txt', {
            'file_id': file_id,
            'mapping_id': mapping_id,
            'error_message': error_message
        })
        subject = settings.ZOOM_TASK_EMAIL_MAPPING_FAILED_SUBJECT

    # Default receiver if ZZ email
    receiver = settings.ZOOM_TASK_EMAIL_RECEIVER

    try:
        mapping = Mapping.objects.get(id=mapping_id)

        # User email or ZZ email
        receiver = mapping.session_email \
            if mapping.session_email else settings.ZOOM_TASK_EMAIL_RECEIVER

    except Mapping.DoesNotExist:
        pass

    send_mail(
        subject,
        template,
        settings.ZOOM_TASK_EMAIL_SENDER,
        [receiver, ],
        fail_silently=False,
    )
