from rest_framework.generics import ListCreateAPIView
from api.uploads.serializers import FileSerializer
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import filters
from validate.models import File


class UploadsCreateList(ListCreateAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('file', 'created')

    fields = (
        'file',
        )

    def perform_create(self, serializer):
        serializer.save(file=self.request.data.get('file'))