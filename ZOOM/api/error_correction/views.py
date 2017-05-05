from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from error_correction.error_correction import error_correction


@api_view(['POST'])
def ErrorCorrectionView(request):
    context = error_correction(request)
    return Response(context)
