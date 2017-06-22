import numpy as np
import pandas as pd
from lib.tools import identify_col_dtype
from file_upload.models import File
from file_upload.models import FileDtypes
from lib.common import get_dictionaries, save_validation_data, get_headings_data_model


def validate(file_id):
    """Perform validation check on file.
    
    Args:
        file_id (str): ID of file.
        
    Returns: 
        context ({str:data}): information related to the validation of file.
    """

    print("Begining Validation")
    
    newdoc = [''] ### Future: using array in case user uploads multiple files
    found_mapping = [] ### Future: automatic mapping ### 

    newdoc[0] = str(File.objects.get(id=file_id).file)

    ### Future: loop here if uploaded multiple files or distrubute with tasks

    df_file = pd.read_csv(newdoc[0])
    
    print("Getting Error Information")
    error_data, dtypes_dict = generate_error_data(df_file)
    zip_list, summary_results, summary_indexes, remaining_mapping = get_headings_data_model(df_file, dtypes_dict)
    print("Saving Error Information")
    save_validation_data(error_data, file_id, dtypes_dict)
    context = {
        'success': 1, 
        "found_list": zip_list, 
        "summary":zip(summary_indexes, summary_results),
        "missing_list" : remaining_mapping
    }

    return context


def generate_error_data(df_file):
    """Get error data for file.
    
    Args:
        df_file (Dataframe): data of csv file in a dataframe.

    Returns: 
        error_data ({str:[str]}): error data for each column.
        dtypes_dict ({str:str}): stores the data-types for each heading.
    """

    file_heading_list = df_file.columns
    dicts, _ = get_dictionaries()
    dtypes_dict = {}
    error_data = {}

    for heading in file_heading_list:
        prob_list, error_count = identify_col_dtype(df_file[heading], heading, dicts)
        dtypes_dict[heading] = prob_list
        error_data[heading] = error_count

    return error_data, dtypes_dict
