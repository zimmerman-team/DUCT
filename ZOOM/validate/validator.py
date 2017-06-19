import numpy as np
import pandas as pd
from lib.tools import identify_col_dtype
from file_upload.models import File
from file_upload.models import FileDtypes
from indicator.models import IndicatorDatapoint
from lib.common import get_dictionaries, save_validation_data


def validate(file_id):
    """Perform validation check on file.
    
    Args:
        file_id (str): ID of file.
        
    Returns: 
        context ({str:data}): information related to the validation of file.
    """

    print("Begining Validation")
    
    newdoc = [''] ### Future: using array in case user uploads multiple files
    remaining_mapping = []
    data_model_headings = []
    found_mapping = [] ### Future: automatic mapping ### 

    newdoc[0] = str(File.objects.get(id=file_id).file)

    ### Future: loop here if uploaded multiple files or distrubute with tasks

    df_file = pd.read_csv(newdoc[0])
    
    #Get datapoint headings
    for field in IndicatorDatapoint._meta.fields:
        data_model_headings.append(field.name)#.get_attname_column())

    #skip first four headings as irrelevant to user input, should use filter for this
    data_model_headings = data_model_headings[4:len(data_model_headings)] 
    remaining_mapping = data_model_headings
    print("Getting Error Information")
    error_data, zip_list, summary_results, summary_indexes, dtypes_dict = generate_error_data(df_file)
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
        zip_list: ([str, str, int]), contains file heading, list of dtypes for heading, amount of empty results.
        summary_results ([str]): summary results of data.
        summary_indexes ([str]): summary headings for data.
        dtypes_dict ({str:str}): stores the data-types for each heading.
    """

    file_heading_list = df_file.columns
    dicts, _ = get_dictionaries()
    dtypes_dict = {}
    error_data = {}
    validation_results = []
    dtypes_list = []
    summary_results = []
    summary_indexes = []

    for heading in file_heading_list:
        prob_list, error_count = identify_col_dtype(df_file[heading], heading, dicts)
        dtypes_dict[heading] = prob_list
        error_data[heading] = error_count
        validation_results.append(df_file[heading].isnull().sum())
        dtypes_list.append(prob_list)
        column_detail = df_file[heading].describe()
        summary_results.append(np.array(column_detail).astype('str'))
        summary_indexes.append(list(column_detail.index))

    zip_list = zip(file_heading_list, dtypes_list, validation_results)

    return error_data, zip_list, summary_results, summary_indexes, dtypes_dict
