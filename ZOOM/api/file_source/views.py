from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from indicator.models import FileSource, FileTags
from .serializers import FileSourceSerializer, FileTagsSerializer



class FileSourceListView(ListAPIView):

    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer


class FileSourceDetailView(RetrieveUpdateDestroyAPIView):

    queryset = FileSource.objects.all()
    serializer_class = FileSourceSerializer   


class TagsListView(ListCreateAPIView):

    queryset = FileTags.objects.all()
    serializer_class = FileTagsSerializer

    def get_queryset(self):
        return self.queryset.filter(file_id_id=self.kwargs.get('file_source_pk'))

    def perform_create(self, serializer):
        print("Here in file_source")
        file_id = get_object_or_404(
            FileSource, pk = self.kwargs.get('file_source_pk')
            )
        serializer.save(file_id=file_id)




