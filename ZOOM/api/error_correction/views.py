from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from error_correction.error_correction import *


@api_view(['POST'])
def ErrorCorrectionView(request):
    if 'save' in request.data:#split into views
    	context = update(request)
    elif 'get_errors' in request.data:
    	context = get_errors(request)
    else:	
    	context = error_correction(request)
    return Response(context)
