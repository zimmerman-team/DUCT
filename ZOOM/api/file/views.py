import json
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import filters

from file_upload.models import File, FileSource, FileTag
from api.file.serializers import FileSerializer, FileSourceSerializer, FileTagSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from file_upload.models import File, FileTag, FileSource


class FileView(APIView):

    parser_classes = (MultiPartParser, FormParser,)
    
    def post(self, request):
        file = self.request.data.get('file')
        file_name = self.request.data.get('file_name')
        description = self.request.data.get('description')
        title = self.request.data.get('title')
        
        try:
            instance= File(file=file, title=title, description=description, file_name=file_name)
            instance.save()
        except:
            context = {"error": "Error occured when saving file."}
            return Response(context)

        tags = request.data.get('tags')
        if tags:
            tags = json.loads(tags)
            for i in range(len(tags)):
                tag = tags[str(i)]["tag"]
                file_tag,_ = FileTag.objects.get_or_create(tag=tag)
                instance.tags.add(file_tag)

        data_source = self.request.data.get('data_source')
        FileSource.objects.get_or_create(name=data_source)

        context = {
          "id": instance.id,
          "title": instance.title,
          "description": instance.description,
          "file": instance.filename(),
          "file_name": instance.file_name,
          "in_progress": instance.in_progress,
          "source_url": instance.source_url,
          "data_source": data_source,
          "tags": tags,
          "created": instance.created,
          "modified": instance.modified,
          "rendered": instance.rendered
        }
        return Response(context)


class FileListView(ListAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer

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


class FileDetailView(ListAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer   

    def get_queryset(self):
        return self.queryset.filter(pk=self.kwargs.get('pk'))


class FileSourceListView(ListCreateAPIView):

    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer


class FileTagListView(ListCreateAPIView):

    queryset = FileTag.objects.all()
    serializer_class = FileTagSerializer




