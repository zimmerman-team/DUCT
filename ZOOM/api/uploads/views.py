from rest_framework import viewsets
# from rest_framework.generics import ListCreateAPIView
from api.uploads.serializers import FileSerializer
from rest_framework.parsers import FormParser, MultiPartParser
from validate.models import File


# class FileViewset(viewsets.ModelViewSet):

#     queryset = File.objects.all()
#     serializer_class = FileSerializer

#     fields = (
#         'id',
#         'file',
#         )


class FilesCreateList(viewsets.ModelViewSet):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)

    fields = (
        'file',
        )

    def perform_create(self, serializer):
        serializer.save(file=self.request.data.get('file'))