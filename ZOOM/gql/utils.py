import json
import logging
import os
import random
import string

from graphene_django.forms.converter import convert_form_field
import django.forms
import django_filters

import graphene
import pydash
from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.contrib.sessions.backends.db import SessionStore
from django.db import models
from django.db.models import Avg, Count, Max, Min, Q, Sum
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from gql.big_feature_generator.big_feature_generator import BigFeatureGenerator

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
        return [self.FIELDS_MAPPING.get(field) for field in kwargs['fields']] if 'fields' in kwargs else []

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
        missing_fields = list(set(requested_fields) - set(groups))
        missing_field_aggr = {}

        # so here we form the array aggregation parameters for the fields
        # that are NOT in the groupBy query, they should be returned
        # as arrays for the filtered data points
        for field in missing_fields:
            missing_field_aggr[field] = ArrayAgg(field, distinct=True)

        if 'geoJsonUrl' in kwargs and kwargs['geoJsonUrl'] and 'filters__name' in groups:
            # so if the data for geojson needs to be dissagregated by sub-indicators(filters)
            # we'll apply a different aggregation logic for geojsons feature processing
            # to work faster in when using multiprocessing parallel
            # so we'll get the arrays of sub-indicators(filters) for our grouped datapoint
            missing_field_aggr['filters__name'] = ArrayAgg('filters__name')
            # and we'll get the arrays of values for these sub-indicators
            missing_field_aggr['value'] = ArrayAgg('value')
            # we'll also need the NOT distinct value format types
            # for the data to be shown correctly
            missing_field_aggr['value_format__type'] = ArrayAgg('value_format__type')
            # and we'll remove the filters__name from the group by so that
            # values would be added for the whole indicator, as thats what we need
            # for the layers themselves
            groups.remove('filters__name')
            #  aand we remove the aggregation as we'll aggregate this ourselves
            aggregations = {}

        if or_filters:
            return self.Model.objects.filter(Q(**filters) | Q(**or_filters))\
                .values(*groups).annotate(**aggregations, **missing_field_aggr).order_by(*orders)

        return self.Model.objects.filter(**filters).values(*groups).annotate(
            **aggregations,
            **missing_field_aggr
        ).order_by(*orders)

    def get_nodes(self, context, **kwargs):
        results = self.get_results(context, **kwargs)
        fields_to_return = kwargs['fields'] if 'fields' in kwargs else kwargs['groupBy']
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
        # this variable will be only used for geoJson file forming
        country_layers = {
            "type": 'FeatureCollection',
            "features": []
        }
        min_value = 0
        max_value = 0

        result_count = results.count()
        # so if a geoJsonUrl was requested(mainly used for the geoJson layers for the map)
        # we will form a json object and save it to a file
        if 'geoJsonUrl' in kwargs and kwargs['geoJsonUrl'] and result_count > 0:
            process_amount = 1
            if result_count > 40000:
                process_amount = settings.POCESS_WORKER_AMOUNT

            feature_generator = BigFeatureGenerator(all_results=results,
                                                    result_count=result_count,
                                                    process_amount=process_amount)

            country_layers['features'] = feature_generator.generate_features()
            min_value = feature_generator.min_value
            max_value = feature_generator.max_value
        else:
            for result in results:
                node = self.__class__(**{field: result[
                    self.FIELDS_MAPPING.get(
                        field)] for field in fields_to_return})

                for field, value in node.__dict__.items():
                    if type(value) in [MultiPolygon, Polygon, Point]:
                        setattr(node, field, value.json)

                for field in aggregation:
                    f = field[field.find('(') + 1:field.rfind(')')]
                    setattr(node, f, result[f])
                # else we form the nodes normally
                nodes.append(node)

        if 'geoJsonUrl' in kwargs and kwargs['geoJsonUrl'] and len(country_layers['features']) > 0:
            unique_count = 0
            # so after we're done forming the geoJson we update
            # the percentiles of the properties
            # and generate the count of uniqValues
            # for coloring purposes
            country_layers['features'] = pydash.arrays.sort(
                country_layers['features'], key=lambda featz: featz['properties']['value'])

            current_value = country_layers['features'][0]['properties']['value']

            for index, feat in enumerate(country_layers['features']):
                if current_value != feat['properties']['value']:
                    unique_count += 1
                    current_value = feat['properties']['value']

                country_layers['features'][index]['properties']['percentile'] = unique_count

            # and now when everything has been formed correctly
            # we write the geoJson into a file
            # and add the unique layer node to the nodes
            # response

            if 'currentGeoJson' in kwargs and kwargs['currentGeoJson'] is not None:
                # so we will remove the previous geojson and generate a new one
                file_name = kwargs['currentGeoJson']
                file_url = 'static/temp_geo_jsons/' + file_name
                full_path_to_file = os.path.join(settings.BASE_DIR, file_url)
                if os.path.exists(full_path_to_file):
                    os.remove(full_path_to_file)

            # we ofcourse generate a random string for this
            # geojson file name of ours, so that it wouldn't
            # collide with others
            letters = string.ascii_lowercase
            file_key = ''.join(random.choice(letters) for i in range(50))

            file_name = 'geo_json{file_key}.json'.format(file_key=file_key)

            file_url = 'static/temp_geo_jsons/' + file_name

            full_path_to_file = os.path.join(settings.BASE_DIR, file_url)

            with open(full_path_to_file, 'w') as json_file:
                json.dump(country_layers, json_file)

            node = self.__class__(geoJsonUrl=file_url, uniqCount=unique_count,
                                  minValue=min_value, maxValue=max_value)

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

        return session_store['session_email'] if 'session_email' in session_store \
            else settings.ZOOM_TASK_EMAIL_RECEIVER

    except Exception as e:
        # Maybe this user is admin, so can access without token
        logging.exception(e)

        return None


def generate_list_filter_class(inner_type):
    form_field = type(
        "List{}FormField".format(inner_type.__name__),
        (django.forms.Field,),
        {},
    )
    filter_class = type(
        "{}ListFilter".format(inner_type.__name__),
        (django_filters.Filter,),
        {
            "field_class": form_field,
            "__doc__": (
                "{0}ListFilter is a small extension "
                "of a raw django_filters.Filter "
                "that allows us to express graphql List({0}) "
                "arguments using FilterSets."
            ).format(inner_type.__name__),
        },
    )
    convert_form_field.register(form_field)(
        lambda x: graphene.List(inner_type, required=x.required)
    )

    return filter_class


StringListFilter = generate_list_filter_class(graphene.String)
