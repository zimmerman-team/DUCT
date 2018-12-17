import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from django.db import models
from django.db.models import Count, Sum, Min, Max, Avg
import pandas as pd
import datetime

class OrderedDjangoFilterConnectionField(DjangoFilterConnectionField):

    @classmethod
    def connection_resolver(
            cls, resolver, connection, default_manager, max_limit,
            enforce_first_or_last, filterset_class, filtering_args,
            root, info, **args):

        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        qs = default_manager.get_queryset() \
            if hasattr(default_manager, 'get_queryset') else default_manager

        qs = filterset_class(data=filter_kwargs, queryset=qs).qs
        order = args.get('orderBy', None)

        if order:
            qs = qs.order_by(*order)

        return super(DjangoFilterConnectionField, cls).connection_resolver(
            resolver, connection, qs, max_limit,
            enforce_first_or_last, root, info, **args
        )


class AggregationNode(graphene.ObjectType):
    FIELDS_MAPPING = {}
    FIELDS_FILTER_MAPPING = {}
    Model = models.Model

    class Meta:
        interfaces = (relay.Node, )

    def get_group_by(self, context, **kwargs):
        return [self.FIELDS_MAPPING.get(field) for field in kwargs['groupBy']]

    def get_order_by(self, context, **kwargs):
        return [('-' if '-' == field[0] else '') + self.FIELDS_MAPPING
                .get(field.replace('-', '')) for field in kwargs['orderBy']]

    def get_filters(self, context, **kwargs):
        filters = {}
        for field,filter_field in self.FIELDS_FILTER_MAPPING.items():
            value = kwargs.get(field)
            if value:
                filters[filter_field] = value

        return filters

    def get_aggregations(self, context, **kwargs):
        start = '('
        end = ')'
        return {
            field[field.find(start) + len(start):field.rfind(end)]:
                eval(field[:field.find(start) + 1] + '"' +
                     self.FIELDS_MAPPING.get(
                         field[field.find(start) + len(start):field.rfind(end)]
                ) + '"' + field[-1:]) for field in kwargs['aggregation']
        }

    def get_results(self, context, **kwargs):
        filters = self.get_filters(context, **kwargs)

        groups = self.get_group_by(context, **kwargs)
        show = groups.copy()
        show.append('id')
        show.append('value')

        orders = self.get_order_by(context, **kwargs)

        aggregations = self.get_aggregations(context, **kwargs)

        if 'filters__name' in filters:
            filter_list = filters.pop('filters__name', None)
            queryset = self.Model.objects.filter(**filters).prefetch_related('filters')
            for filter in filter_list:
                queryset = queryset.filter(filters__name=filter)
            df = pd.DataFrame(list(queryset.values(*show)))
        else:
            df = pd.DataFrame(list(self.Model.objects.filter(**filters).prefetch_related('filters').values(*show)))

        if 'filters__name' in groups:
            f1 = lambda x: ', '.join(list(x.filters.all().values_list('name', flat=True)))
            df['filters__name'] = list(map(f1,  queryset))

        df = df.sort_values(orders)

        #Here check aggrgeation
        df = pd.DataFrame({'value': df.groupby(groups)['value'].sum()}).reset_index()

        return df.to_dict(orient='records')#queryset_og.annotate(**aggregations).order_by(*orders)

    def get_nodes(self, context, **kwargs):
        results = self.get_results(context, **kwargs)
        nodes = []
        aggregation = kwargs['aggregation']
        for result in results:
            node = self.__class__(**{field: result[
                self.FIELDS_MAPPING.get(
                    field)] for field in kwargs['groupBy']})

            for field in aggregation:
                f = field[field.find('(') + 1:field.rfind(')')]
                setattr(node, f, result[f])

            nodes.append(node)

        return nodes
