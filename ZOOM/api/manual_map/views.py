from rest_framework.response import Response
from rest_framework.decorators import api_view
from lib.manual_mapper import manual_mapper


@api_view(['GET', 'POST'])
def manual_mapping(request):
    if request.method == 'POST':
        context = manual_mapper(request.data)
        return Response(context)
    else:
        return Response("No file selected");
