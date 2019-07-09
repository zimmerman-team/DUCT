import logging

import graphene
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.sessions.backends.db import SessionStore
from django.db import models
from django.db.models import Avg, Count, Max, Min, Q, Sum
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

email_session_key = None


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

    def get_requested_fields(self, context, **kwargs):
        requested_fields = []

        for selection in context.field_asts[0].selection_set.selections:
            if self.FIELDS_MAPPING.get(selection.name.value) != 'value':
                requested_fields.append(self.FIELDS_MAPPING.get(selection.name.value))

        return requested_fields

    def get_requested_names(self, context, **kwargs):
        requested_names = []

        for selection in context.field_asts[0].selection_set.selections:
            if self.FIELDS_MAPPING.get(selection.name.value) != 'value':
                requested_names.append(selection.name.value)

        return requested_names

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
        requested_fields = self.get_requested_fields(context, **kwargs)
        missing_fields = list(set(requested_fields).symmetric_difference(groups))
        missing_field_aggr = {}

        # so here we form the array aggregation parameters for the fields
        # that are NOT in the groupBy query, they should be returned
        # as arrays for the filtered data points
        for field in missing_fields:
            missing_field_aggr[field] = ArrayAgg(field, distinct=True)

        if or_filters:
            return self.Model.objects.filter(Q(**filters) | Q(**or_filters))\
                .values(*groups).annotate(**aggregations, **missing_field_aggr).order_by(*orders)

        return self.Model.objects.filter(**filters).values(*groups).annotate(
            **aggregations,
            **missing_field_aggr
        ).order_by(*orders)

    def get_nodes(self, context, **kwargs):
        results = self.get_results(context, **kwargs)
        requested_names = self.get_requested_names(context, **kwargs)
        # so here we'll want to return data points with the unique
        # indicators specified, so mainly this is used to avoid
        # indicators with duplicate names, so that their datapoints values
        # would not get aggregated when they're filtered by indicator name
        if 'unique_indicator' in kwargs and kwargs['unique_indicator'] and results.count() > 0:
            indicator_ids = []
            indicator_names = []
            # oke so first we get the unique id's of the datapoints indicators and their names
            unique_id_tuple = list(results.values_list('indicator__name', 'indicator__id', named=True).distinct())
            for item_tuple in unique_id_tuple:
                ind_name = getattr(item_tuple, 'indicator__name')
                # so yeah basically because we're working with duplicate names
                # and in the results there might be indicators with different names
                # we just need to weeed out the duplicate names, and save the
                # leftover ids, and refilter that result query, by NOT duplicate
                # indicator name ids == ezi
                if ind_name not in indicator_names:
                    indicator_names.append(ind_name)
                    indicator_ids.append(getattr(item_tuple, 'indicator__id'))

            results = results.filter(indicator__id__in=indicator_ids)

        nodes = []
        aggregation = kwargs['aggregation']
        for result in results:

            node = self.__class__(**{field: result[
                self.FIELDS_MAPPING.get(
                    field)] for field in requested_names})

            for field, value in node.__dict__.items():
                if type(value) in [MultiPolygon, Polygon, Point]:
                    setattr(node, field, value.json)

            for field in aggregation:
                f = field[field.find('(') + 1:field.rfind(')')]
                setattr(node, f, result[f])

            nodes.append(node)

        return nodes


def set_session_email(session_email):
    # Save email verified to the session
    # to use it in other view
    session_store = SessionStore()
    session_store['session_email'] = session_email
    session_store.save()

    # Expose the session key to use in other view
    # This is needed to assign variable email_session_key in other module,
    # so it can be used as a global variable,
    # please find which module call this function and follow the logic
    return session_store.session_key


def get_session_email():
    # Save email verified to the session
    # to use it in other view
    try:
        session_store = SessionStore(session_key=email_session_key)

        return session_store['session_email']

    except Exception as e:
        # Maybe this user is admin, so can access without token
        logging.exception(e)

        return None
