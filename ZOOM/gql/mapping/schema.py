import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, NumberFilter, CharFilter

from mapping.models import Mapping


class MappingNode(DjangoObjectType):
    entry_id = graphene.String()

    class Meta:
        model = Mapping
        interfaces = (relay.Node, )

    def resolve_entry_id(self, context, **kwargs):
        return self.id


class MappingFilter(FilterSet):
    entry_id = NumberFilter(method='filter_entry_id')
    entry_id__in = CharFilter(method='filter_entry_id__in')

    class Meta:
        model = Mapping
        fields = {
            'file_source': ['exact', 'in'],
        }

    def filter_entry_id(self, queryset, name, value):
        name = 'id'
        return queryset.filter(**{name: value})

    def filter_entry_id__in(self, queryset, name, value):
        name = 'id__in'
        return queryset.filter(**{name: eval(value)})


class Query(object):
    mapping = relay.Node.Field(MappingNode)
    all_mappings = DjangoFilterConnectionField(
        MappingNode, filterset_class=MappingFilter
    )
