import os
import logging
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from metadata.models import File, FileSource
from indicator.models import Datapoints
from api.file.serializers import FileSerializer, FileSourceSerializer


class FileListView(ListCreateAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)

    fields = (
        'id',
        'title',
        'description',
        'file',
        'file_name',
        'in_progress',
        'source_url',
        'data_source',
        'status',
        'authorised',
        'tags',
        'created',
        'modified',
        'rendered')

    def perform_create(self, serializer):
        try:
            serializer.save(
                file=self.request.data.get('file'), 
                file_name=self.request.data.get('file_name')
            )
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception("--Problem saving file")
            context = {}
            context['error'] = "Error occured when saving file"
            context['success'] = 0
            raise #temp 


@api_view(['POST'])
def update_status(request):
    try:
        print("File status ")
        file = File.objects.get(id=request.data['file_id'])
        file.status = request.data['status']
        file.save()
    except Exception as e:
            logger = logging.getLogger("django")#don't need the logger
            logger.exception("--Error in updating status of file")
            context = {}
            context['error'] = "Error occured when updating status of file"
            context['success'] = 0
            raise #temp 
    return Response({"success":1})


class FileDetailView(RetrieveUpdateDestroyAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer 

    def perform_update(self, serializer):

        pk = self.kwargs.get('pk')

        file = File.objects.get(pk=pk)
        file.title = self.request.data.get('title')
        file.description = self.request.data.get('description')
        file.authorised = self.request.data.get('authorised')

        data_source = self.request.data.get('data_source')
        file.status = self.request.data.get('status')

        if data_source: 
            data_source_obj, data_source_created = FileSource.objects.get_or_create(name=data_source)
            file.data_source = data_source_obj
        
        file.save()

    def delete(self, request, *args, **kwargs):

        try:
            file_object = self.get_object()
            file_dtypes = file_object.datatypes_overview_file_location
            
            for i in file_dtypes:
                path = i.dtype_name
                if path:
                    try:
                        os.remove(path)
                    except Exception:
                        continue

                path = i.dtype_dict_name
                if path:
                    try:
                        os.remove(path)
                    except Exception:
                        continue
        except:
            logger = logging.getLogger("django")
            logger.exception("--Error when deleting file")
            context = {}
            context['error'] = "Error when deleting file"
            context['success'] = 0
            raise #temp 

        return self.destroy(request, *args, **kwargs)


class FileSourceListViewPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'

class FileSourceListView(ListCreateAPIView):

    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer
    pagination_class = FileSourceListViewPagination

@api_view(['POST'])
def add_remove_source(request):
    try:
        if request.data['action'] == "save":
            _, created = FileSource.objects.get_or_create(name=request.data['source'])
        else:#delete
            FileSource.objects.get(name=request.data['source']).delete()
    except Exception as e:
        logger = logging.getLogger("django")
        logger.exception("--Error when removing source")
        context = {}
        context['error'] = "Error when removing source"
        context['success'] = 0
        raise #temp 

    return Response({"success": 1})