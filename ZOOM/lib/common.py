from file_upload.models import File, FileDtypes
import pickle
import pandas as pd
import json


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


def get_data(file_id):
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