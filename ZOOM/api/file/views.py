from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import filters

from file_upload.models import File, FileSource, FileTag
from api.file.serializers import FileSerializer, FileSourceSerializer, FileTagSerializer


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
        'tags',
        'created',
        'modified',
        'rendered')

    def perform_create(self, serializer):
        serializer.save(file=self.request.data.get('file'), file_name=self.request.data.get('file_name'))


class FileDetailView(RetrieveUpdateDestroyAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer   


class FileSourceListView(ListAPIView):

    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer


class FileTagListView(ListCreateAPIView):

    queryset = FileTag.objects.all()
    serializer_class = FileTagSerializer

    def get_queryset(self):
        return self.queryset.filter(file_id=self.kwargs.get('file_source_pk'))

    def perform_create(self, serializer):
        file_id = get_object_or_404(
            FileSource, pk = self.kwargs.get('file_source_pk'))
        serializer.save(file_id=file_id)


