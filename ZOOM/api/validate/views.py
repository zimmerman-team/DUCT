
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import os

from lib.tools import check_file_formatting, check_file_type
from validate.models import File
from validate.validator import validate

class Validate(APIView):
    def post(self, request):
        if request.method == 'POST':
            file_id = request.data.get('file_id')
        else:
            return Response("No file selected")
        context = validate(file_id)
        return Response(context)


@api_view(['POST'])
def error_correction(request):
    context = {"Error": "To do"}
    return Response(context)        


@api_view(['POST'])
def check_file_valid(request):
    file_name = str(File.objects.get(id=request.data['file_id']).file_name)
    file_loc = str(File.objects.get(id=request.data['file_id']).file)

    result = check_file_type(file_name)

    if not result[0]:
        os.remove(file_loc) 
        File.objects.get(id=request.data['file_id']).delete()
        return Response(result[1])

    result = check_file_formatting(file_loc)
    if not result[0]:
        os.remove(file_loc) 
        File.objects.get(id=request.data['file_id']).delete()
        return Response(result[1])

    #lazy, fix this to include all errors at once
    return Response({"success": 1})
    
