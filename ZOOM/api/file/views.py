from api.file.models import File, upload_to
from api.file.serializers import FileSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from django.http import JsonResponse
#from validate.models import File, upload_to #old file model

class FileList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        #fill in for returning list if files
        return Response({'File': 'List Files'}, status=200)
        #return Response(json.dumps(workspace))

    #post functions for file
    def post(self, request, format=None):
        if 'save' in request.data:
            #check if file exists, it it doesn't continue
            file_name = request.data['file_name']
            file_contents = request.data['file']
            result = self.save_file(file_name, file_contents)
        return Response({'result': result})
    
    def save_file(self, file_name, file_contents):
        file_contents = file_contents.split('|')#use more unique character??
        file_contents = file_contents[1:(len(file_contents)-1)]
        f = open(upload_to(None, file_name), 'w')
        for line in file_contents: 
            f.write((str(line).encode('utf-8')) + '\n')  # python will convert \n to os.linesep
        f.close()
        instance = File(file = file_name)
        instance.save()
        return True



class FileDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        #try:
        #    return File.objects.get(pk=pk)
        #except File.DoesNotExist:
        #    raise Http404
        return Response("Test")

    def get(self, request, pk, format=None):
        #file = self.get_object(pk)
        #serializer = FileSerializer(file)
        #eturn Response(workspace)
        return Response("Test")

    def put(self, request, pk, format=None):
       file = self.get_object(pk)
        
        #serializer = FileSerializer(file, data=request.data)
        
        #if serializer.is_valid():
            #serializer.save()
            #return Response(serializer.data)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        file = self.get_object(pk)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)