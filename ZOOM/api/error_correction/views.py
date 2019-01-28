import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from error_correction.utils import *


@api_view(['POST'])
def error_correction_view(request):
    context = {}
    logger = logging.getLogger("django")
    if request.data['update']:  # split into views
        try:  # useful for individual error handling
            context = update(
                request.data['file_id'],
                request.data['update_data'])
        except Exception as e:
            logger.exception("--Error in updating file in error correction")
            context['error'] = "Error occurred when updating file"
            context['success'] = 0
            raise
    elif request.data['delete']:
        try:
            context = delete_data(
                request.data['file_id'],
                request.data['delete_data'])
        except Exception as e:
            logger.exception(
                "--Error in deleting data from file in error correction")
            context['error'] = "Error occurred when deleting data from file"
            context['success'] = 0
            raise
    elif request.data['error_toggle']:
        try:
            context = get_errors(request.data)
            request.data['error_data'] = context
        except Exception as e:
            logger.exception("--Error when retrieving errors")
            context['error'] = "Error occurred when retrieving errors"
            context['success'] = 0
    context = error_correction(request.data)

    return Response(context)
