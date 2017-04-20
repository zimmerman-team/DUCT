from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from error_correction.error_correction import error_correction


@api_view(['GET', 'POST'])
def ErrorCorrectionView(request):
    if request.method == 'POST':
        context = error_correction(request)
        return Response(context)
    else:
        return Response("No file selected");

