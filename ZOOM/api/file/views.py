from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import api_view

from file_upload.models import File, FileSource, FileTag
from indicator.models import IndicatorDatapoint
from api.file.serializers import FileSerializer, FileSourceSerializer, FileTagSerializer
import os

import json

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
        'tags',
        'created',
        'modified',
        'rendered')

    def perform_create(self, serializer):
        serializer.save(
            file=self.request.data.get('file'), 
            file_name=self.request.data.get('file_name')
        )

        # tags = self.request.data.get('tags')

        # if tags:
        #     tags = json.loads(tags)
        #     for i in range(len(tags)):
        #         tag = tags[i]["tag"]
        #         file_tag, file_tag_created = FileTag.objects.get_or_create(name=tag)
        #         file.tags.add(file_tag)

        # data_source = self.request.data.get('data_source')
        # data_source_obj, data_source_created = FileSource.objects.get_or_create(name=data_source)

        # file.data_source = data_source_obj 
        # file.save()




    #def delete(self, request): getting front end error, permission denied for delete method  <- @Kieran - ListCreateAPIView does not allow delete indeed, should use the FileDetailView endpoint for delete, but your method above is ok for now :) http://www.django-rest-framework.org/api-guide/generic-views/#listcreateapiview 
    #    print("In self")


@api_view(['POST'])
def update_status(request):
    file = File.objects.get(id=request.data['file_id'])
    file.status = request.data['status']
    file.save()
    return Response({"success":1})
    
class FileDetailView(RetrieveUpdateDestroyAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer 

    def perform_update(self, serializer):

        pk = self.kwargs.get('pk')

        file = File.objects.get(pk=pk)
        file.tags = []

        # update tags / source
        tags = self.request.data.get('tags')

        if tags:
            for i in range(len(tags)):
                tag = tags[i]
                file_tag, file_tag_created = FileTag.objects.get_or_create(name=tag)
                file.tags.add(file_tag)

        file.title = self.request.data.get('title')
        file.description = self.request.data.get('description')

        data_source = self.request.data.get('data_source')
        print("----------------- data source -----------------")
        print(self.request.data.get('status'))
        print(self.request.data)
        file.status = self.request.data.get('status')
        data_source_obj, data_source_created = FileSource.objects.get_or_create(name=data_source)

        file.data_source = data_source_obj 
        file.save()


class FileSourceListView(ListCreateAPIView):

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

