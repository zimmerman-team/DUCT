import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from django.db import models
from django.db.models import Count, Sum, Min, Max, Avg
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.db.models import Q


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
    FIELDS_OR_FILTER_MAPPING = {}
    FIELD_OR_RELATED_MAPPING = {}
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
        for field, filter_field in self.FIELDS_FILTER_MAPPING.items():
            value = kwargs.get(field)
            if value:
                filters[filter_field] = value

        return filters

    def get_or_filters(self, context, **kwargs):
        filters = self.get_filters(context, **kwargs)

        for field in filters.copy():
            for or_filter, related_field in \
                    self.FIELD_OR_RELATED_MAPPING.items():
                if field == related_field:
                    del filters[field]

        or_filters = {}
        for field, filter_field in self.FIELDS_OR_FILTER_MAPPING.items():
            value = kwargs.get(field)
            if value:
                or_filters[filter_field] = value

        if or_filters and filters:
            return {**filters, **or_filters}

        return or_filters

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
        or_filters = self.get_or_filters(context, **kwargs)
        groups = self.get_group_by(context, **kwargs)
        orders = self.get_order_by(context, **kwargs)
        aggregations = self.get_aggregations(context, **kwargs)

        if or_filters:
            return self.Model.objects.filter(Q(**filters) | Q(**or_filters))\
                .values(*groups).annotate(**aggregations).order_by(*orders)

        return self.Model.objects.filter(**filters).values(*groups).annotate(
            **aggregations
        ).order_by(*orders)

    def get_nodes(self, context, **kwargs):
        results = self.get_results(context, **kwargs)
        nodes = []
        aggregation = kwargs['aggregation']
        for result in results:
            node = self.__class__(**{field: result[
                self.FIELDS_MAPPING.get(
                    field)] for field in kwargs['groupBy']})

            for field, value in node.__dict__.items():
                if type(value) in [MultiPolygon, Polygon, Point]:
                    setattr(node, field, value.json)

            for field in aggregation:
                f = field[field.find('(') + 1:field.rfind(')')]
                setattr(node, f, result[f])

            nodes.append(node)

        return nodes
