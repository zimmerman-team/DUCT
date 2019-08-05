import logging
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.metadata.serializers import FileSerializer, FileSourceSerializer
from geodata.models import Geolocation
from gql.views import requires_scope
from metadata.models import File, FileSource


class FileListView(ListCreateAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)

    fields = (
        'id',
        'title',
        'description',
        'contains_subnational_data',
        'organisation',
        'maintainer',
        'date_of_dataset',
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
            data['location'] = Geolocation.objects.get(id=data['location'])
            data['source'] = FileSource.objects.get(id=data['source'])
            serializer.save(**data.dict())
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception("--Problem saving file")
            context = {}
            context['error'] = "Error occured when saving file"
            context['success'] = 0
            raise  # temp


class FileDetailView(RetrieveUpdateDestroyAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer

    def perform_update(self, serializer):
        pk = self.kwargs.get('pk')
        file = File.objects.filter(pk=pk)
        source = self.request.data.get('source')
        location = self.request.data.get('location')
        data = self.request.data

        if source:
            obj = FileSource.objects.get(id=source)
            data['source'] = obj

        if location:
            obj = Geolocation.objects.get(id=location)
            data['location'] = obj

        file.update(**data)
        # file.save()

    def delete(self, request, *args, **kwargs):

        try:
            file_object = self.get_object()
        except BaseException:
            logger = logging.getLogger("django")
            logger.exception("--Error when deleting file")
            context = {}
            context['error'] = "Error when deleting file"
            context['success'] = 0
            raise  # temp

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
        'id',
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
            context['error'] = \
                "Error occured when saving source. " \
                "Check if source already exists"
            context['success'] = 0
            raise


class FileSourceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer

    def delete(self, request, *args, **kwargs):
        try:
            file_source_object = self.get_object()
        except BaseException:
            logger = logging.getLogger("django")
            logger.exception("--Error when deleting file source")
            context = {}
            context['error'] = "Error when deleting file source"
            context['success'] = 0
            raise  # temp

        return self.destroy(request, *args, **kwargs)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, )

    @requires_scope()
    def post(self, request):
        file_obj = request.FILES['file']
        if 'id' in request.data:
            file = File.objects.get(request.data['id'])
            file.file = file_obj
            file.save()
        else:
            location = os.path.join(settings.MEDIA_ROOT, settings.DATASETS_URL)

            fs = FileSystemStorage(location=location)
            filename = fs.save(file_obj.name, file_obj)

            old_name = location + filename
            new_name = location + filename + '.new.csv'

            old_file = open(old_name, encoding="ascii", errors="ignore")
            new_file = open(new_name, "w")
            new_file.write(old_file.read())

            file_url = '{dataset_url}{filename}'.format(
                dataset_url=settings.DATASETS_URL,
                filename=filename + '.new.csv'
            )

            return Response(data={"url": file_url}, status=202)
