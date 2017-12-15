from __future__ import division
from django.db import connection,transaction
from django.conf import settings
from django.http import Http404
import numpy as np
import pandas as pd
import pickle 
import json
import datetime
import time
import os
import math

from dateutil.parser import parse
from indicator.models import *
from geodata.models import Country
from lib.converters import convert_to_JSON
from lib.tools import check_column_data_type, correct_data, convert_df
from lib.common import get_file_data, get_dtype_data, save_mapping, get_dictionaries
from file_upload.models import File
from validate.validator import generate_error_data, save_validation_data
from api.indicator.views import reset_mapping
import time

def manual_mapper(data):
    """Perfoms manual mapping process."""
    if 'dict' in data:
        """print("###########################################################")
        print("Data")
        print(data)"""
        order = {}
        index_order = {}
        bulk_list = []
        file_id = data['file_id']
        mappings = data['dict']
        save_mapping(file_id, mappings)

        unit_of_measure_value = mappings.pop("empty_unit_of_measure", None)
        empty_values_array = [mappings.pop("empty_indicator", None), mappings.pop("empty_country", None), mappings.pop("empty_indicator_cat", None),
                                unit_of_measure_value, mappings.pop("empty_date", None)]
        relationship_dict = mappings.pop("relationship", None)
        left_over_dict = mappings.pop("left_over", None)
        df_data = get_file_data(file_id)
        error_data, dtypes_dict = get_dtype_data(file_id)
        print("Begining Mapping")
        print (time.strftime("%H:%M:%S"))
        print(relationship_dict)
        print(left_over_dict)

        ###If column mapped to multiple sections in data model
        if relationship_dict:
            relationship_dict = clean_data(relationship_dict, "~", " ")
            left_over_dict = clean_data(left_over_dict, "~", " ")
            
        ###Start checking the keys 
        for key in mappings:
            if mappings[key]:#this is included incase no mapping is given
                if len(mappings[key]) > 1:#greated than one for subgroups change for indicator scenario
                    if key == "indicator_category":
                       df_data, mappings, dtypes_dict, tmp_mapping = group_indicator_categories(df_data, mappings, dtypes_dict, relationship_dict,key)
                else:
                    mappings[key][0] = mappings[key][0].replace("~", " ")

        df_data, mappings, dtypes_dict = apply_missing_values(df_data, mappings, dtypes_dict, empty_values_array)

        ###Convert csv
        if relationship_dict:
            #check if unit of measure exists

            df_data, dtypes_dict, mappings = convert_df(mappings, relationship_dict, left_over_dict, df_data, dtypes_dict, unit_of_measure_value)

        print("Validating data")
        for key in mappings:
            if mappings[key]:
                if key in mappings[key]:
                    mappings[key] = [key]
                if not mappings[key][0] in df_data.columns:
                    mappings[key][0] = mappings[key][0].replace("~", " ")

        print("Corrceting dtypes")
        result, correction_mappings, context = check_mapping_dtypes(mappings, dtypes_dict)
        
        ###Checking if mapping is bad or not
        if not result:
            return context

        print("Getting Error types")###needed?
        error_lines, new_dtypes_dict = generate_error_data(df_data)
        save_validation_data(error_lines, file_id, new_dtypes_dict)
        ###Combine dictionaries
        for key in new_dtypes_dict:
            dtypes_dict[key] = new_dtypes_dict[key] 

        reverse_mapping = {}
        for key in mappings:
            if mappings[key]:
                index_order[key] = mappings[key][0]
                reverse_mapping[mappings[key][0]] = key 

        df_data = correct_data(df_data, correction_mappings, error_lines, index_order)
        ###Clear data structures
        correction_mappings = None
        error_lines = None
        null_values = df_data[mappings['indicator_category'][0]].isnull()
        df_data[mappings['indicator_category'][0]][null_values] = "Default"
        print("Filtering NaNs from measure value, indicator, data and country")
        filter_applied = (df_data[index_order['indicator']].notnull() & df_data[index_order['date_value']].notnull() 
                        & df_data[index_order['measure_value']].notnull() & df_data[index_order['country']].notnull())
        
        df_data = df_data[filter_applied].reset_index()
        file = File.objects.get(id=file_id)
        index_order['file'] = "file"
        reverse_mapping['file'] = "file"
        date_object = datetime.datetime.now()
        index_order['date_created'] = "date_created"
        reverse_mapping['date_created'] = "date_created"
        instance = Time(date_type = "YYYY")#temp
        instance.save()
        index_order['date_format'] = 'date_format'
        reverse_mapping['date_format'] = 'date_format'
        
        df_data['file'] = df_data[df_data.columns[0]]
        df_data['file'] = file
        df_data['date_created'] =  df_data[df_data.columns[0]]
        df_data['date_created'] = date_object
        ###Future figure out format
        df_data['date_format'] = df_data[df_data.columns[0]]
        df_data['date_format'] = instance

        print("Save indicators, sources, categories, countries")
        ind_dict, ind_cat_dict, ind_source_dict, ind_country_dict = get_save_unique_datapoints(df_data, index_order)
        dicts = [ind_dict, ind_cat_dict, ind_source_dict, ind_country_dict]
        save_datapoints(df_data, index_order, reverse_mapping, dicts)
        
        context = {"success" : 1}
        return context
    else :
        context = {"error_messages" : "No data in dictionary sent", "success" : 0}
        return context


def clean_data(data, unwanted_str, replace_str):
    """Begins process for grouping indicator categories together.
    
    Args:
        data ([],{}): data to be cleaned.
        unwanted_str (str): string value to be replaced.
        replace_str (str): string value to be inserted.

    Returns: 
        data ([],{}): returns a cleaned version of the data.
    """
    for i in data:
        value = data.pop(i)
        key = i.replace(unwanted_str, replace_str)
        data[key] = value
    return data

def group_indicator_categories(df_data, mappings, dtypes_dict, relationship_dict, key):
    """Begins process for grouping indicator categories together.
    
    Args:
        df_data (Dataframe): dataframe of CSV file.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        relationship_dict ({str: [str]}): section of the data model mapped to a file heading.
        key (str): file heading.

    Returns: 
        df_data (Dataframe): dataframe of CSV file.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        tmp_mappings ([str]): if a file heading is mapped to multiple parts of
                              the data model, create an array of headings for 
                              the relationship creation method.
    """

    #ignore relationship

    df_data["indicator_category"] = ""
    tmp_mappings = ['indicator_category']
    count = 0
    for value in mappings[key]:
        mappings[key][count] = mappings[key][count].replace("~", " ")
        value = value.replace("~", " ")

        #loop through data combine with heading name and itself   
        if not value == 'indicator_category':
            if not relationship_dict:#no relationshup defined
                    df_data["indicator_category"] = df_data["indicator_category"] + "|" + value + ": " + df_data[value].map(str)
            else:
                if not (value in relationship_dict):
                    df_data["indicator_category"] = df_data["indicator_category"] + "|" + value + ": " + df_data[value].map(str)
                else:
                    tmp_mappings.append(value)     
        count += 1
    mappings[key] = tmp_mappings#IF RELATIONSHOip add here????
    dtypes_dict[mappings['indicator_category'][0]] = [('str','str')]

    return df_data, mappings, dtypes_dict, tmp_mappings


def apply_missing_values(df_data, mappings, dtypes_dict, empty_values_array):
    """Appliess missing values to dataframe.
    
    Args:
        df_data (Dataframe): dataframe of CSV file.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        empty_values_array ([str]): values related to missing values in manual mapping process

    Returns: 
        df_data (Dataframe): dataframe of CSV file.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
    """
    indicator_value, country_value, indicator_category_value, unit_of_measure_value, value_of_date = empty_values_array

    if indicator_value:
        mappings['indicator'] = ['indicator']
        df_data['indicator'] = indicator_value
        dtypes_dict[mappings['indicator'][0]] = [('text', 'text')]
        #add indicator value as column 

    if country_value:
        mappings['country'] = ['country']
        df_data['country'] = country_value
        dtypes_dict[mappings['country'][0]] = [('country(iso2)', 'country(iso2)')]

    if indicator_category_value:
        mappings['indicator_category'] = ['indicator_category']
        df_data['indicator_category'] = indicator_category_value
        dtypes_dict[mappings['indicator_category'][0]] = [('text', 'text')]

    if value_of_date:
        mappings['date_value'] = ['date_value']
        df_data['date_value'] = value_of_date
        dtypes_dict[mappings['date_value'][0]] = [('date', 'date')]

    if unit_of_measure_value:
        if len(unit_of_measure_value.keys()) < 2 :#chect each entry emoty unit_of measure a dict
            mappings['unit_of_measure'] = ['unit_of_measure']
            df_data['unit_of_measure'] = unit_of_measure_value[unit_of_measure_value.keys()[0]]
            dtypes_dict[mappings['unit_of_measure'][0]] = [('text', 'text')]
        else:
            mappings['unit_of_measure'] = ['unit_of_measure']
            dtypes_dict[mappings['unit_of_measure'][0]] = [('text', 'text')]

    return df_data, mappings, dtypes_dict

def check_mapping_dtypes(mappings, dtypes_dict):
    """Begins process of checking if mapped columns are suitable.
    
    Args:
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.

    Returns: 
        result: indicates whether there is a bad mapping or not.
        correction_mappings ({str:(str,str)}): the conversion needed for each file heading.
        context ({str:[data]}): the information displayed to the user if mapping is bad.
    """
    print("Checking data types")
    correction_mappings = {}
    error_message = []

    for key in mappings:
            if mappings[key]:#this is included incase no mapping is given
                correction_mappings[mappings[key][0]] = []
                temp_results_check_dtype, temp_found_dtype, temp_convert_dtype = check_column_data_type(key, dtypes_dict[mappings[key][0]])

                if temp_results_check_dtype != False:
                    correction_mappings[mappings[key][0]] = (temp_found_dtype, temp_convert_dtype) 
                else:
                    error = [mappings[key][0], key, temp_found_dtype, temp_convert_dtype]
                    error_message.append(error)#datatype blah blah 

    context = {"error_messages" : error_message, "success" : 0}
    return (not len(error_message) > 0), correction_mappings, context 


def get_save_unique_datapoints(df_data, index_order):
    """Gets foreign keys for IndicatorDatapoint and saves new entries if needed.
    
    Args:
        df_data (Dataframe): dataframe of CSV file.
        index_order ({str:[str]}): data model section and associated column heading.

    Returns: 
        ind_dict ({str:Indicator}): dictionary of Indicator objects.
        ind_cat_dict ({str:IndicatorCategory}): dictionary of IndicatorCategory objects.
        ind_source_dict ({str:IndicatorSource}): dictionary of IndicatorSource objects.
        ind_country_dict ({str:Country}): dictionary of Country objects.
    """

    count  = 0
    ind_dict = {}
    ind_cat_dict = {}
    ind_source_dict = {}
    ind_country_dict = {}
    unique_indicator = [] 
    unique_indicator_cat = [] 
    unique_indicator_source = []
    unique_country = []

    if "indicator" in index_order:
        unique_indicator = df_data[index_order["indicator"]].unique()
    if "indicator_category" in index_order:
        unique_indicator_cat = df_data.groupby([index_order["indicator"],index_order["indicator_category"]]).size().reset_index()
    if "source" in index_order:
        unique_indicator_source = df_data.groupby([index_order["indicator"],index_order["source"]]).size().reset_index()
    if "country" in index_order:
        unique_country = df_data[index_order['country']].unique()
    unique_lists = [unique_indicator, unique_indicator_cat, unique_indicator_source, unique_country]
    count = 0

    for unique_list in unique_lists:
        for i in range(len(unique_list)):
            if(count == 0):#indicator
                instance, created = Indicator.objects.get_or_create(id=unique_list[i])
                if not instance:
                    instance = created
                    instance.save()
                ind_dict[unique_list[i]] = instance
            elif(count == 1):#indicator_cat
                if "|" in unique_list[index_order['indicator_category']][i]:
                    cats = sorted(list(filter(None, np.unique(np.array(unique_list[index_order['indicator_category']][i].split("|"))))))
                    temp_id = ind_dict[unique_list[index_order['indicator']][i]].id + ("".join(cats[0]))
                    parent, created = IndicatorCategory.objects.get_or_create(unique_identifier= temp_id,
                                                                            name=cats[0], 
                                                                            indicator = ind_dict[unique_list[index_order['indicator']][i]],
                                                                            level=0)
                    if not parent:
                        parent = created  

                    for j in range(1 , len(cats)):                    
                        temp_id = ind_dict[unique_list[index_order['indicator']][i]].id + ("".join(cats[0:j+1]))
                        parent, created = IndicatorCategory.objects.get_or_create(unique_identifier=temp_id,
                                                                                name=cats[j], 
                                                                                indicator = ind_dict[unique_list[index_order['indicator']][i]],
                                                                                parent = parent,
                                                                                level=j)
                        if not parent:
                            parent = created
                    finstance = parent
                else:
                    temp_id = ind_dict[unique_list[index_order['indicator']][i]].id + (unique_list[index_order['indicator_category']][i])
                    finstance, created = IndicatorCategory.objects.get_or_create(unique_identifier=temp_id,
                                                                                name = unique_list[index_order['indicator_category']][i], 
                                                                                indicator = ind_dict[unique_list[index_order['indicator']][i]], 
                                                                                level=0)
                    if not finstance:
                        finstance = created          
                ind_cat_dict[unique_list[index_order['indicator']][i] + unique_list[index_order['indicator_category']][i]] = finstance####wrong here
            elif(count == 2):#ind_source
                instance = IndicatorSource.objects.filter(id = unique_list[index_order['source']][i].decode(errors='ignore'), indicator = ind_dict[unique_list[index_order['indicator']][i]]).first() 
                if not instance:
                    instance = IndicatorSource(id = unique_list[index_order['source']][i].decode(errors='ignore'), indicator = ind_dict[unique_list[index_order['indicator']][i]])
                    instance.save()
                ind_source_dict[unique_list[index_order['indicator']][i] + unique_list[index_order['source']][i]] = instance
            else:
                instance = Country.objects.filter(code = unique_list[i])
                ind_country_dict[unique_list[i]] = instance[0]#shold use get?
        count += 1

    return ind_dict, ind_cat_dict, ind_source_dict, ind_country_dict

def save_datapoints(df_data, index_order, reverse_mapping, dicts):
    """Saves each line that is valid of csv file to data model.
    
    Args:
        df_data (Dataframe): data of csv file in a dataframe.
        index_order ({str: str}): contains data points as headings and columns as values.
        reverse_mapping ({str: str}): inverse of index_order.
        dicts ([str:{str:Model}]): list of dictionaries containing foreign keys.
    """

    file_source = df_data['file'][0].data_source 
    ind_dict, ind_cat_dict, ind_source_dict, ind_country_dict = dicts
    df_data[index_order['indicator_category']] = df_data[index_order['indicator']] + df_data[index_order['indicator_category']]
    df_data[index_order['indicator_category']] = df_data[index_order['indicator_category']].map(ind_cat_dict)
    if 'source' in index_order:
        df_data[index_order['source']] = df_data[index_order['indicator']] + df_data[index_order['source']]
        df_data[index_order['source']] = df_data[index_order['source']].map(ind_source_dict)
    df_data[index_order['indicator']] = df_data[index_order['indicator']].map(ind_dict)
    df_data[index_order['country']] = df_data[index_order['country']].map(ind_country_dict)
    df_data = df_data[reverse_mapping.keys()]#should do this earlier
    df_data = df_data.rename(index=str, columns=reverse_mapping)#rename columns to data model
    data_to_save = df_data.to_dict(orient='records') 
    f = (lambda x: IndicatorDatapoint(**x) )
    vfunc = np.vectorize(f)
    bulk_list = vfunc(np.array(data_to_save))
    print("Bulk saving")

    batch_size = int(math.ceil(len(bulk_list)/100000))
    print(len(bulk_list))
    print(len(bulk_list)/100000)
    print(batch_size)
    previous_batch = 0
    next_batch = 0
    for i in range(1,batch_size + 1):
        next_batch += 100000 
        if next_batch > len(bulk_list):
            next_batch = len(bulk_list)
            i = batch_size + 1
        IndicatorDatapoint.objects.bulk_create(list(bulk_list)[previous_batch : next_batch])
        print("Num ", i)
        print("Previous batch ", previous_batch)
        print("Next batch ", next_batch)
        bulk_list[previous_batch:next_batch] = None #release memory
        previous_batch = next_batch

    for i in ind_dict:
        ind_dict[i].count = IndicatorDatapoint.objects.filter(indicator=(ind_dict[i])).count()
        ind_dict[i].file_source = file_source
        ind_dict[i].save()
        x.all()

'''Remaps all files that have been mapped'''
def remap_all_files():
    #from django.http import QueryDict
    #dict = {'a': 'one', 'b': 'two', }
    #qdict = QueryDict('', mutable=True)
    #qdict.update(dict)

    files = File.objects.all()
    for file in files:
        if file.status == 5:
            context = {'data':{'file': str(file.id)}}
            reset_mapping(json.dumps(context, ensure_ascii=False))#encoding error
            context = {'data' : {'file_id' : str(file.id), 'dict' : json.loads(file.mapping_used)}}
            manual_mapper(context)

