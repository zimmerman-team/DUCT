import json

import graphene
import pandas as pd
from django_filters import CharFilter, FilterSet, NumberFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from indicator.models import MAPPING_DICT
from metadata.models import File, FileSource


class FileSourceNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = FileSource
        interfaces = (relay.Node, )

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class FileSourcFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = FileSource
        fields = {
            'name': ['exact', 'icontains', 'istartswith', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class FileNode(DjangoObjectType):
    entry_id = graphene.String()
    file_heading_list = graphene.JSONString()
    data_model_heading = graphene.JSONString()

    class Meta:
        model = File
        interfaces = (relay.Node, )

    def resolve_entry_id(self, context, **kwargs):
        return self.id

    def resolve_file_heading_list(self, context, **kwargs):
        return json.loads(self.file_heading_list)

    def resolve_data_model_heading(self, info):
        return pd.Series(MAPPING_DICT).to_json()


class FileFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = File
        fields = {
            'title': ['exact', 'icontains', 'istartswith', 'in'],
            'description': ['exact', 'icontains', 'istartswith', 'in'],
            'contains_subnational_data': ['exact', ],
            'organisation': ['exact', 'icontains', 'istartswith', 'in'],
            'maintainer': ['exact', 'icontains', 'istartswith', 'in'],
            'date_of_dataset':  ['exact', 'gte', 'lte'],
            'methodology': ['exact', 'icontains', 'istartswith', 'in'],
            'define_methodology': ['exact', 'icontains', ],
            'update_frequency': ['exact', 'icontains', ],
            'comments': ['exact', 'icontains', ],
            'accessibility':  ['exact', 'in', ],
            'data_quality': ['exact', 'in', ],
            'number_of_rows': ['gte', 'lte', ],
            'number_of_rows_saved': ['gte', 'lte', ],
            'file_types': ['exact', 'in', ],
            'data_uploaded': ['exact', 'gte', 'lte', ],
            'last_updated': ['exact', 'gte', 'lte', ]
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class Query(object):
    file_source = relay.Node.Field(FileSourceNode)
    all_file_sources = DjangoFilterConnectionField(
        FileSourceNode, filterset_class=FileSourcFilter
    )

    file = relay.Node.Field(FileNode)
    all_files = DjangoFilterConnectionField(
        FileNode, filterset_class=FileFilter
    )
