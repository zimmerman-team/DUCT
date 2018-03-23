from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from error_correction.error_correction import *
import logging
import datetime

@api_view(['POST'])
def ErrorCorrectionView(request):
    context = {}
    logger = logging.getLogger("django")
    if 'save' in request.data:#split into views
        try:#useful for individual error handling
            context = update(request)
        except Exception as e:
            logger.exception("--Error in updating file in error correction")
            context['error'] = "Error occured when updating file"
            context['success'] = 0
            raise #temp	
    elif 'delete' in request.data:
        try:
            context = delete_data(request)
        except Exception as e:
            logger.exception("--Error in deleting data from file in error correction")
            context['error'] = "Error occured when deleting data from file"
            context['success'] = 0
            raise #temp		
    elif 'get_errors' in request.data:
        try:
            context = get_errors(request)
        except Exception as e:
            logger.exception("--Error when retrieving errors")
            context['error'] = "Error occured when retrieving errors"
            context['success'] = 0
    else:	
        context = error_correction(request)
    
    return Response(context)