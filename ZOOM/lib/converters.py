import os
from flattentool.json_input import BadlyFormedJSONError
import logging
import shutil
import warnings
import flattentool
import json
import pandas as pd
import numpy as np
from indicator.models import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lib.exceptions import CoveInputDataError

logger = logging.getLogger(__name__)

#recieved data as pandas dataframe
def convert_to_JSON(indicator1, indicator2):
    query1 = IndicatorDatapoint.objects.filter(indicator_id=indicator1)
    #indicator1_id = Indicator.objects.get(pk=indicator1) # identify which manager you want
    #query1  = indicator1_id.IndicatorDatapoint_set.all()  # retrieve all related HostData objects
    #query2 = IndicatorDatapoint.objects.get(indicator=inidcator2)
    json_str = """{
                    "data" : {
                    "source" : "Stata Data",
                    "name" : "DataSet",
                    "data" : [ \n"""
    #include population
    counter = 0
    cat = []

    for query in query1:
        country_id = query.country_id
        query2 = IndicatorDatapoint.objects.filter(indicator_id=indicator2, country_id = country_id)

        if query2 and not (">" in query.indicator_category_id.id):
            counter += 1
            json_str += """{ "Category" : "%s", """ % (query.indicator_category_id.id)
            json_str += """ "%s" : %s, """ % (query.indicator_id.id, query.measure_value)
            json_str += """ "%s" : %s, """ % (query2[0].indicator_id.id, query2[0].measure_value)
            json_str += """ "country" : "%s" },\n""" % (country_id.id)
            cat.append(query.indicator_category_id.id)
        counter +=1
    json_str = json_str[:-2]
    
            #json_str += 
            #json_str += """ "%s" : %d, """ % (query2.indicator, query2.measure_value)
    #json_str += """{ Category : %s, """ % (query1[counter-1].indicator_category_id.id)
    #json_str += """{ "%s" : %s, """ % (query1[counter - 1].indicator_id.id, query1[counter - 1].measure_value)
    #json_str += """ "%s" : %s, """ % (query2[0].indicator_id.id, query2[0].measure_value)
    #json_str += """ "country" : "%s" } \n""" % (country_id.id)

    json_str += """ ]}, "firstRecordId" : 1,
                   "lastRecordId" : %d, """ % (counter)
    json_str += """ "variableIndices" : [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 ], """ #not sure about these
    json_str += """ "variableIsString" : {
                "%s" : false,
                "%s" : false,
                "%s" : false """ % ("Category", indicator1, indicator2) 
    json_str += """ },
                  "variableNames" : [ "%s", "%s" ],
                  "variableLabels" : {
                    "%s" : "%s",
                    "%s" : "%s",
                    "country" : "Country Name"
                  }, """ % ( indicator1, indicator2, indicator1, indicator1, indicator2, indicator2,   )
    
    cat = np.unique(cat)
    json_str += """ "valueLabelNames" : {
                    "Category" : "Category",
                    "micrank" : "micrank"
                  },
                  "valueLabels" : { "Category" : {"""
    counter = 0
    for item in cat:
        json_str += """ "%s" : "%s",""" % (item, item)
        counter += 1
    json_str = json_str[:-1]
    json_str += "}," 
    json_str += """ "micrank" : {"""
    counter = 0
    for item in cat:
        json_str += """ "%d" : "%d",""" % (counter + 1, counter + 1)
        counter += 1
    json_str = json_str[:-1]
    json_str += "} }," 




    #},"   
                  #  },
   #                 "micrank" : {
   #                   "1" : "1",
   #                   "2" : "2",
    #                  "3" : "3"
    #                } """              
    json_str += """ "numberOfRecords" : 1,
                  "numberOfVariables" : 2 }"""

    f = open(os.getcwd() + '/static/data/msas.json', 'w')
    f.write(json_str)  # python will convert \n to os.linesep
    f.close()  # you can omit in most cases as the destructor will call it
    #with open(os.getcwd() + "/msas(copy).json", 'w') as file: #'../static/data/msas(copy).json'
    #    file.write("here")
        #file.write(json_str)

  
#cover methods
def convert_spreadsheet(request, data, file_type):
    context = {}
    converted_path = os.path.join(data.upload_dir(), 'unflattened.json')

    cell_source_map_path = os.path.join(data.upload_dir(), 'cell_source_map.json')
    heading_source_map_path = os.path.join(data.upload_dir(), 'heading_source_map.json')
    encoding = 'utf-8'
    
    if file_type == 'csv':
        # flatten-tool expects a directory full of CSVs with file names
        # matching what xlsx titles would be.
        # If only one upload file is specified, we rename it and move into
        # a new directory, such that it fits this pattern.
        input_name = os.path.join(data.upload_dir(), 'csv_dir')
        os.makedirs(input_name) ##Making directory here
        destination = input_name #os.path.join(input_name, request.cove_config['root_list_path'] + '.csv')
        #destination = os.path.join(input_name, request.cove_config['root_list_path'] + '.csv')#request.cove_config??
        shutil.copy(data.file.name, destination) # not sure what this is for
        
        try:
            with open(destination, encoding='utf-8') as main_sheet_file:
                main_sheet_file.read()
        except UnicodeDecodeError:
            try:
                with open(destination, encoding='cp1252') as main_sheet_file:
                    main_sheet_file.read()
                encoding = 'cp1252'
            except UnicodeDecodeError:
                encoding = 'latin_1'
    else:
        input_name = data.file.name
            #f.write("input name 1 : " + str(input_name))
    try:
        conversion_warning_cache_path = os.path.join(data.upload_dir(), 'conversion_warning_messages.json')
        if not os.path.exists(converted_path) or not os.path.exists(cell_source_map_path):
            with warnings.catch_warnings(record=True) as conversion_warnings:
                flattentool.unflatten(
                    input_name,
                    output_name=converted_path,
                    input_format=file_type,
                    root_list_path=request.cove_config['root_list_path'],
                    root_id=request.cove_config['root_id'],
                    schema=request.cove_config['schema_url'] + request.cove_config['item_schema_name'],
                    convert_titles=True,
                    encoding=encoding,
                    cell_source_map=cell_source_map_path,
                    heading_source_map=heading_source_map_path,
                )
                context['conversion_warning_messages'] = [str(w.message) for w in conversion_warnings]
            with open(conversion_warning_cache_path, 'w+') as fp:
                json.dump(context['conversion_warning_messages'], fp)
        elif os.path.exists(conversion_warning_cache_path):
            with open(conversion_warning_cache_path) as fp:
                context['conversion_warning_messages'] = json.load(fp)

        context['converted_file_size'] = os.path.getsize(converted_path)
    except Exception as err:
        logger.exception(err, extra={
            'request': request,
            })
        raise CoveInputDataError({
            'sub_title': _("Sorry we can't process that data"),
            'link': 'cove:index',
            'link_text': _('Try Again'),
            'msg': _('We think you tried to supply a spreadsheet, but we failed to convert it to JSON.\n\nError message: {}'.format(repr(err)))
        })

    context.update({
        'conversion': 'unflatten',
        'converted_path': converted_path,
        'converted_url': '{}/unflattened.json'.format(data.upload_url())
    })
    return context


def convert_json(request, data):
    context = {}
    converted_path = os.path.join(data.upload_dir(), 'flattened')
    flatten_kwargs = dict(
        output_name=converted_path,
        main_sheet_name=request.cove_config['root_list_path'],
        root_list_path=request.cove_config['root_list_path'],
        root_id=request.cove_config['root_id'],
        schema=request.cove_config['schema_url'] + request.cove_config['item_schema_name'],
    )
    try:
        conversion_warning_cache_path = os.path.join(data.upload_dir(), 'conversion_warning_messages.json')
        if not os.path.exists(converted_path + '.xlsx'):
            with warnings.catch_warnings(record=True) as conversion_warnings:
                if request.POST.get('flatten'):
                    flattentool.flatten(data.original_file.file.name, **flatten_kwargs)
                else:
                    return {'conversion': 'flattenable'}
                context['conversion_warning_messages'] = [str(w.message) for w in conversion_warnings]
            with open(conversion_warning_cache_path, 'w+') as fp:
                json.dump(context['conversion_warning_messages'], fp)
        elif os.path.exists(conversion_warning_cache_path):
            with open(conversion_warning_cache_path) as fp:
                context['conversion_warning_messages'] = json.load(fp)
        context['converted_file_size'] = os.path.getsize(converted_path + '.xlsx')

        conversion_warning_cache_path_titles = os.path.join(data.upload_dir(), 'conversion_warning_messages_titles.json')

        if request.cove_config['convert_titles']:
            with warnings.catch_warnings(record=True) as conversion_warnings_titles:
                flatten_kwargs.update(dict(
                    output_name=converted_path + '-titles',
                    use_titles=True
                ))
                if not os.path.exists(converted_path + '-titles.xlsx'):
                    flattentool.flatten(data.original_file.file.name, **flatten_kwargs)
                    context['conversion_warning_messages_titles'] = [str(w.message) for w in conversion_warnings_titles]
                    with open(conversion_warning_cache_path_titles, 'w+') as fp:
                        json.dump(context['conversion_warning_messages_titles'], fp)
                elif os.path.exists(conversion_warning_cache_path_titles):
                    with open(conversion_warning_cache_path_titles) as fp:
                        context['conversion_warning_messages_titles'] = json.load(fp)

            context['converted_file_size_titles'] = os.path.getsize(converted_path + '-titles.xlsx')

    except BadlyFormedJSONError as err:
        raise CoveInputDataError(context={
            'sub_title': _("Sorry we can't process that data"),
            'link': 'cove:index',
            'link_text': _('Try Again'),
            'msg': _('We think you tried to upload a JSON file, but it is not well formed JSON.\n\nError message: {}'.format(err))
        })
    except Exception as err:
        logger.exception(err, extra={
            'request': request,
            })
        return {
            'conversion': 'flatten',
            'conversion_error': repr(err)
        }
    context.update({
        'conversion': 'flatten',
        'converted_path': converted_path,
        'converted_url': '{}/flattened'.format(data.upload_url())
    })
    return context
