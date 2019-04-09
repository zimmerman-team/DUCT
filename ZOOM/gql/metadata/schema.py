import json

import graphene
import pandas as pd
from django_filters import CharFilter, FilterSet, NumberFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from indicator.models import MAPPING_DICT
from metadata.models import File, FileSource, FileTags, SurveyData
from error_correction.utils import ERROR_CORRECTION_DICT


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
            'date_of_dataset': ['exact', 'gte', 'lte'],
            'methodology': ['exact', 'icontains', 'istartswith', 'in'],
            'define_methodology': ['exact', 'icontains', ],
            'update_frequency': ['exact', 'icontains', ],
            'comments': ['exact', 'icontains', ],
            'accessibility': ['exact', 'in', ],
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


class FileTagsNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = FileTags
        interfaces = (relay.Node, )

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class FileTagsFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = FileTags
        fields = {
            'name': ['exact', 'icontains', 'istartswith', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class SurveyDataNode(DjangoObjectType):
    entry_id = graphene.String()
    have_you_tested_tool = graphene.String()
    who_did_you_test_with = graphene.String()
    considered_senstive = graphene.String()
    staff_trained = graphene.String()
    ask_sensitive = graphene.String()
    select_respondents = graphene.String()
    edit_sheet = graphene.String()
    data_cleaning_techniques = graphene.String()

    class Meta:
        model = SurveyData
        interfaces = (relay.Node,)

    def resolve_entry_id(self, context, **kwargs):
        return self.id

    def resolve_have_you_tested_tool(self, context, **kwargs):
        return str(self.have_you_tested_tool)

    def resolve_who_did_you_test_with(self, context, **kwargs):
        return str(self.who_did_you_test_with)

    def resolve_considered_senstive(self, context, **kwargs):
        return str(self.considered_senstive)

    def resolve_staff_trained(self, context, **kwargs):
        return str(self.staff_trained)

    def resolve_ask_sensitive(self, context, **kwargs):
        return str(self.ask_sensitive)

    def resolve_select_respondents(self, context, **kwargs):
        return str(self.select_respondents)

    def resolve_edit_sheet(self, context, **kwargs):
        return str(self.edit_sheet)

    def resolve_data_cleaning_techniques(self, context, **kwargs):
        return str(self.data_cleaning_techniques)


class SurveyDataFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = SurveyData
        fields = {
            'have_you_tested_tool': [
                'exact', 'in'
            ],
            'who_did_you_test_with': [
                'exact', 'in'
            ],
            'staff_trained': [
                'exact', 'in'
            ],
            'ask_sensitive': [
                'exact', 'in'
            ],
            'select_respondents': [
                'exact', 'in'
            ],
            'other_respondent': [
                'exact', 'in'
            ],
            'how_many_respondents': [
                'exact', 'in'
            ],
            'edit_sheet': [
                'exact', 'in'
            ],
            'data_cleaning_techniques': [
                'exact', 'in'
            ],
            'other_cleaning_technique': [
                'exact', 'in'
            ],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class FileErrorCorrectionNode(DjangoObjectType):
    entry_id = graphene.String()
    command = graphene.JSONString()

    class Meta:
        model = File
        interfaces = (relay.Node, )
        only_fields = ('id', )

    def resolve_entry_id(self, context, **kwargs):
        return self.id

    def resolve_command(self, info):
        ERROR_CORRECTION_DICT['file_id'] = self.id
        return pd.Series(ERROR_CORRECTION_DICT).to_json()


class FileErrorCorrectionFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = File
        fields = {}

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

    file_tags = relay.Node.Field(FileTagsNode)
    all_file_tags = DjangoFilterConnectionField(
        FileTagsNode, filterset_class=FileTagsFilter
    )

    survey_data = relay.Node.Field(SurveyDataNode)
    all_survey_datas = DjangoFilterConnectionField(
        SurveyDataNode, filterset_class=SurveyDataFilter
    )

    file_error_correction = relay.Node.Field(FileErrorCorrectionNode)
    all_file_error_correction = DjangoFilterConnectionField(
        FileErrorCorrectionNode, filterset_class=FileErrorCorrectionFilter
    )
