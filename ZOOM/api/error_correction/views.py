from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from error_correction.error_correction import *
import logging
import datetime

@api_view(['POST'])
def ErrorCorrectionView(request):
    if 'save' in request.data:#split into views
        try:
            context = update(request)
        except:
            logger = logging.getLogger("django")
            logger.exception("--------" + str(datetime.datetime.now()) + " Error in updating file in error correction --------")
            context['error'] = "Error occured when updating file"
            context['success'] = 0
            raise #temp	
    elif 'delete' in request.data:
        try:
            context = delete_data(request)
        except:
            logger = logging.getLogger("django")
            logger.exception("--------" + str(datetime.datetime.now()) + " Error in deleting data from file in error correction --------")
            context['error'] = "Error occured when deleting data from file"
            context['success'] = 0
            raise #temp		
    elif 'get_errors' in request.data:
        try:
            context = get_errors(request)
        except:
            logger = logging.getLogger("django")
            logger.exception("--------" + str(datetime.datetime.now()) + " Error when retrieving errors --------")
            context['error'] = "Error occured when retrieving errors"
            context['success'] = 0
    else:	
        context = error_correction(request)
    
    return Response(context)