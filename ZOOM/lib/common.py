from django.conf import settings
from indicator.models import Datapoints, MAPPING_HEADINGS
from metadata.models import File
from geodata.models import Geolocation
import pickle
import pandas as pd
import numpy as np
import json
import os
import uuid
import time


def get_geolocation_dictionary():
    dict = {}
    dict['iso2'] = list(
        Geolocation.objects.values_list(
            'iso2', flat=True).distinct())
    dict['iso2'] = [x for x in dict['iso2'] if x is not None]
    value_dict = {k.lower(): 'iso2' for k in dict['iso2']}
    dict['iso3'] = list(
        Geolocation.objects.values_list(
            'iso3', flat=True).distinct())
    dict['iso3'] = [x for x in dict['iso3'] if x is not None]
    value_dict = {**value_dict, **{k.lower(): 'iso3' for k in dict['iso3']}}
    for entry in list(Geolocation.objects.distinct('type')):
        dict[entry.type] = list(Geolocation.objects.filter(
            type=entry.type).values_list('tag', flat=True).distinct())
        dict[entry.type] = [x for x in dict[entry.type] if x is not None]
        value_dict = {**value_dict,
                      **{k.lower(): entry.type for k in dict[entry.type]}}
    return value_dict


def save_validation_data(error_data, id, dtypes_dict):
    """Saves error data for file.

    Args:
        error_data ({str:[str]}): error data for each column..
        id (str): ID of file being used.
        dtypes_dict ({str:str}): stores the data-types for each heading.
    """

    path = os.path.join(
        os.path.dirname(
            settings.BASE_DIR),
        'ZOOM/media/tmpfiles')
    tmp_id = str(uuid.uuid4())
    error_file = path + "/" + tmp_id + "_error_data.txt"

    with open(error_file, 'wb') as f:
        pickle.dump(error_data, f)

    dtypes_overview = path + "/" + tmp_id + "_dtype_overview.txt"
    with open(dtypes_overview, 'wb') as f:
        pickle.dump(dtypes_dict, f)

    instance = File.objects.get(id=id)

    if instance.datatypes_overview_file_location:
        os.remove(instance.datatypes_overview_file_location)
        os.remove(instance.error_file_location)
    instance.datatypes_overview_file_location = dtypes_overview
    instance.error_file_location = error_file

    instance.save()


def get_dtype_data(id):
    """Get data type data for file.

    Args:
        id (str): ID of file.

    Returns:
        error_data ([[int]]): error data, first list is a column
        ,second is the row.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
    """

    file = File.objects.get(id=id)

    with open(str(file.error_file_location), 'rb') as f:
        dtypes_dict = pickle.load(f)

    with open(str(file.datatypes_overview_file_location), 'rb') as f:
        error_data = pickle.load(f)

    return error_data, dtypes_dict


def get_file_data(id):
    """Gets file in dataframe format"""
    file_name = File.objects.get(id=id).file
    df_data = pd.read_csv(file_name)
    return df_data


def save_mapping(id, instance):
    """Saves user mapping for file"""
    file = File.objects.get(id=id)
    ##Need to make mappings unique
    '''c, created = Mapping.objects.get_or_create(data=json.dumps(mapping))
    if created:
        print('Created new mapping')
        c.save()'''
    c = Mapping(data=json.dumps(mapping))
    c.save()
    file.mapping_used = c
    file.save()


def get_mapping(id):
    """Get user mapping for file"""
    file = File.objects.get(id=id)
    if file.mapping_used:
        return {'success': 1, 'mapping': json.loads(file.mapping_used)}
    return {'success': 0, 'mapping': None}


def get_headings_data_model(df_file):
    """Get column headings and data model headings.

    Args:
        df_file (Dataframe): data of csv file in a dataframe.

    Returns:
        zip_list: ([str, str, int]), contains file headings,
        the rest is information not needed but kept due
        to pre-existing dependency on given data structure.
        summary_indexes ([str]): summary headings for data.
    """

    file_heading_list = df_file.columns
    dtypes_list = file_heading_list
    validation_results = file_heading_list
    data_model_headings = []

    # Get datapoint headings
    for field in Datapoints._meta.fields:
        data_model_headings.append(field.name)#.get_attname_column())
    #skip first four headings as irrelevant to user input, should use filter for this

    data_model_headings = data_model_headings[4:len(data_model_headings)]
    data_model_headings = filter(lambda x: "search_vector_text" != x and
                                 "date_format" != x and
                                 "date_created" != x and
                                 "file" != x, data_model_headings)
    remaining_mapping = data_model_headings
    zip_list = zip(file_heading_list, dtypes_list, validation_results)
    # change this to add hover for file heading
    summary_results = file_heading_list
    summary_indexes = file_heading_list  # change this
    return zip_list, summary_results, summary_indexes, remaining_mapping


def get_column_information(df_file, dtypes_dict):
    """Get information about columns.

    Args:
        df_file (Dataframe): data of csv file in a dataframe.
        dtypes_dict ({str:str}): stores the data-types for each heading.

    Returns:
        zip_list: ([str, str, int]), contains file heading, list of dtypes
        for heading, amount of empty results.
        summary_results ([str]): summary results of data.
        summary_indexes ([str]): summary headings for data.
    """

    file_heading_list = df_file.columns
    validation_results = []
    dtypes_list = []
    summary_results = []
    summary_indexes = []
    data_model_headings = []

    for heading in file_heading_list:
        validation_results.append(df_file[heading].isnull().sum())
        data_str = []
        for types in dtypes_dict[heading]:
            data_str.append("" +
                            str(types[1]) +
                            " of data a " +
                            str(types[0]) +
                            " value.")
        dtypes_list.append(data_str)
        column_detail = df_file[heading].describe()
        summary_results.append(np.array(column_detail).astype('str'))
        summary_indexes.append(list(column_detail.index))

    # Get datapoint headings
    for field in Datapoints._meta.fields:
        data_model_headings.append(field.name)  # .get_attname_column())
    # skip first four headings as irrelevant to user input, should use filter
    # for this

    data_model_headings = MAPPING_HEADINGS.keys()
    remaining_mapping = data_model_headings

    zip_list = zip(file_heading_list, dtypes_list, validation_results)
    return zip_list, summary_results, summary_indexes, \
        remaining_mapping, file_heading_list
