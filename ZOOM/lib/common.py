from django.conf import settings
from indicator.models import IndicatorDatapoint
from file_upload.models import File, FileDtypes
from geodata.models import Country, CountryAltName
import unicodedata
import pickle
import pandas as pd
import numpy as np
import json
import os
import uuid


def get_dictionaries():#might be better to use a set
    """Gets dictionaries for checking country data"""
    iso2_codes = Country.objects.values_list('code')
    iso3_codes = Country.objects.values_list('iso3')
    country_names = Country.objects.values_list('name')
    country_alt_names = CountryAltName.objects.values_list('name')
    data_lists = [iso2_codes, iso3_codes, country_names, country_alt_names]
    source = ["country(iso2)", "country(iso3)", "country(name)", "country(name)"]
    country_source_dict = {}
    country_iso2_dict = {}

    for i in range(len(data_lists)):
        counter = 0
        
        #can vectorise this
        for j in range(len(data_lists[i])):
            
            try:#not needed
                temp_value = str(data_lists[i][j][0].lower())
            except Exception:#special_character
                temp_value = str(unicodedata.normalize('NFKD', data_lists[i][j][0]).lower().encode('ascii','ignore'))
            
            country_source_dict[temp_value] = source[i] #{NL: {iso2: NL, source:iso2}}
            
            if i < (len(data_lists) - 1):
                country_iso2_dict[temp_value] = iso2_codes[j][0]# just iso2 codes
            else:
                country_alt_name = CountryAltName.objects.get(name=data_lists[i][j][0]) 
                country = Country.objects.get(code=country_alt_name.country.code) 
                country_iso2_dict[temp_value] = country.code
    return country_source_dict, country_iso2_dict

def save_validation_data(error_data, file_id, dtypes_dict):
    """Saves error data for file.
    
    Args:
        error_data ({str:[str]}): error data for each column..
        file_id (str): ID of file being used.
        dtypes_dict ({str:str}): stores the data-types for each heading.
    """

    path = os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/tmpfiles')
    dtype_name = path +  "/" + str(uuid.uuid4()) + ".txt"
    with open(dtype_name, 'w') as f:
        pickle.dump(error_data, f)

    dict_name = path +  "/" + str(uuid.uuid4()) + ".txt"
    with open(dict_name, 'w') as f:
        pickle.dump(dtypes_dict, f)
    
    file = File.objects.get(id=file_id)
    #obj, created = FileDtypes.objects.update_or_create(dtype_name=dict_name, file= file) # error due to one to one field

    try:
        instance = FileDtypes.objects.get(file=file)#
        if instance.dtype_name:
            os.remove(instance.dtype_name)
        if instance.dtype_dict_name:
            os.remove(instance.dtype_dict_name)
        instance.dtype_name = dtype_name
        instance.dtype_dict_name = dict_name 
        instance.save()
    except Exception:
        FileDtypes(dtype_name=dtype_name, file=file, dtype_dict_name=dict_name).save()


def get_dtype_data(file_id):
    """Get data type data for file.
    
    Args:
        file_id (str): ID of file.

    Returns: 
        error_data ([[int]]): error data, first list is a column ,second is the row.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
    """

    file_dtypes = FileDtypes.objects.get(file=File.objects.get(id=file_id)) 
    
    with open(str(file_dtypes.dtype_name), 'rb') as f:
        error_data = pickle.load(f)

    with open(str(file_dtypes.dtype_dict_name), 'rb') as f:
        dtypes_dict = pickle.load(f)

    return error_data, dtypes_dict


def get_file_data(file_id):
    """Gets file in dataframe format"""
    file_name = File.objects.get(id=file_id).file
    df_data = pd.read_csv(file_name)
    return df_data


def save_mapping(file_id, mapping):
    """Saves user mapping for file"""
    file = File.objects.get(id=file_id)
    file.mapping_used = json.dumps(mapping)
    file.save()

def get_mapping(file_id):
    """Get user mapping for file"""
    file = File.objects.get(id=file_id)
    if file.mapping_used:
        return {success: 1, mapping: json.loads(file.mapping_used)}
    return {success: 0, mapping: None}

def get_headings_data_model(df_file, dtypes_dict):
    """Get information about columns.
    
    Args:
        df_file (Dataframe): data of csv file in a dataframe.
        dtypes_dict ({str:str}): stores the data-types for each heading.

    Returns: 
        zip_list: ([str, str, int]), contains file heading, list of dtypes for heading, amount of empty results.
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
            data_str.append("" + str(types[1]) + " of data identified as a " + str(types[0]) + " value.")
        dtypes_list.append(data_str)
        print(data_str)
        column_detail = df_file[heading].describe()
        summary_results.append(np.array(column_detail).astype('str'))
        summary_indexes.append(list(column_detail.index))

    print(dtypes_list)
    #Get datapoint headings
    for field in IndicatorDatapoint._meta.fields:
        data_model_headings.append(field.name)#.get_attname_column())
    #skip first four headings as irrelevant to user input, should use filter for this

    data_model_headings = data_model_headings[4:len(data_model_headings)] 
    remaining_mapping = data_model_headings    

    zip_list = zip(file_heading_list, dtypes_list, validation_results)
    print(zip_list)
    return zip_list, summary_results, summary_indexes, remaining_mapping