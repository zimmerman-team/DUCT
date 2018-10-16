import os
import logging
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.pagination import PageNumberPagination

from geodata.models import Geolocation
from metadata.models import File, FileSource
from api.metadata.serializers import FileSerializer, FileSourceSerializer


class FileListView(ListCreateAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)

    fields = (
        'file_id',
        'title',
        'description',
        'contains_subnational_data',
        'organisation',
        'maintainer',
        'data_of_dataset',
        'methodology',
        'define_methodology',
        'update_frequency',
        'comments',
        'accessibility',
        'data_quality',
        'number_of_rows',
        'number_of_rows_saved',
        'file_types',
        'data_uploaded',
        'last_updated',
        'location',
        'source',
        'file',
    )

    def perform_create(self, serializer):
        try:
            data = self.request.data
            data['location'] = Geolocation.objects.get(geolocation_id  = data['location'])
            data['source'] = FileSource.objects.get(file_source_id= data['source'])
            serializer.save(**data.dict())
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception("--Problem saving file")
            context = {}
            context['error'] = "Error occured when saving file"
            context['success'] = 0
            raise #temp


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
    parser_classes = (MultiPartParser, FormParser,)

    fields = (
        'file_source_id',
        'name',
    )

    def perform_create(self, serializer):
        try:
            serializer.save(
                name=self.request.data.get('name'),
            )
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception("--Problem saving source")
            context = {}
            context['error'] = "Error occured when saving source. Check if source already exists"
            context['success'] = 0
            raise


class FileSourceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer

    def delete(self, request, *args, **kwargs):
        try:
            file_source_object = self.get_object()
        except:
            logger = logging.getLogger("django")
            logger.exception("--Error when deleting file source")
            context = {}
            context['error'] = "Error when deleting file source"
            context['success'] = 0
            raise  # temp

        return self.destroy(request, *args, **kwargs)