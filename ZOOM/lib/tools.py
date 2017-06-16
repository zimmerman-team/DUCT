import strict_rfc3339
from functools import wraps  # use this to preserve function signatures and docstrings
from geodata.models import Country
from indicator.models import IndicatorDatapoint
from geodata.models import get_dictionaries
from dateutil.parser import parse
import pandas as pd
import numpy as np
import sys
import unicodedata
from collections import Counter
#import complier

def identify_col_dtype(column_values, file_heading, dicts):
    """Identify the data types for each value in a column.
    
    Args:
        column_values (Series): values related to a column.
        file_heading (str): heading of the column.
        dicts ([{str:str},{str:str}]): dictionaries for iso2 conversion and identifing country data type.

    Returns:
        prob_list ([(str,str)]): a list of tuples containing the data type found and the percentage of data found of that type.
        error_counter ([str]): list of data types found for each cell in the column.      
    """

    reload(sys)
    sys.setdefaultencoding('utf-8')

    dtypes_found = []
    prob_list = []
    error_counter = column_values.astype("str")
    error_counter[:] = np.NaN
    not_null_filter = column_values.notnull()
    numeric_filter = pd.to_numeric(column_values[not_null_filter], errors='coerce').notnull()

    print('#############################')
    print(file_heading)
    ###Checking Date###
    #Numeric check
    print("Date Num Check")
    filter_applied = ((not_null_filter) & (numeric_filter))
    error_counter = check_if_date(file_heading, column_values.astype('str'), filter_applied, error_counter)

    #String check
    print("Data Str Check") 
    filter_applied = ((not_null_filter) & (~numeric_filter))
    error_counter = check_if_date(file_heading, column_values, filter_applied, error_counter)

    ###Country Check###
    if(np.sum(error_counter.notnull()) < len(error_counter)):
        print("Country Check")
        f = (lambda x: str(unicodedata.normalize('NFKD', unicode(x)).lower().encode('ascii','ignore')).strip())
        filter_used = not_null_filter & (~numeric_filter)
        print("Apply Normalisation")
        tmp_country_values = column_values[filter_used].apply(f)
        print("Mapping")
        tmp_country_values = tmp_country_values.map(dicts)
        #get values that are not null => country
        country_filter = tmp_country_values.notnull()
        error_counter[filter_used] = tmp_country_values[country_filter]
    
    ###Clean up###
    print("Blank")
    error_counter[~not_null_filter] = "blank"
    
    print("Str")
    filter_used = (error_counter.isnull()) & (not_null_filter & (~numeric_filter))
    error_counter[filter_used] = "str"
    
    print("Num")
    filter_used = (error_counter.isnull()) & (not_null_filter & numeric_filter)
    error_counter[filter_used] = "num"

    dtypes_found = np.unique(error_counter)
    
    normalisation = float(len(column_values))
    for heading, count in Counter(error_counter).most_common():
        prob_list.append((heading, "{0:.0f}%".format(float(count)/normalisation * 100)))
    
    return prob_list, error_counter
    
def check_if_date(file_heading, column_values, filter_used, error_counter):
    """Check if column values could be a date.
    
    Args:
        file_heading (str): heading of the file.
        column_values (Series): values related to a column.
        filter_used (np[boolean]): the filter to search for.
        error_counter ([int]): error data, a list that will contain all data types for column_values.

    Returns: 
        result (boolean): result of check.
        error_counter ([int]): error data, a list that will contain all data types for column_values. 

    """

    # assuming time or date will have appropiate heading, perhaps a bad assumption
    result = "time" in file_heading.lower() or "date" in file_heading.lower() or "year" in file_heading.lower() or "period" in file_heading.lower()
    if result:
        tmp_data_values = pd.to_datetime(column_values[filter_used], errors = 'coerce')
        date_dtype_values = error_counter[filter_used]
        
        #get values that are not null => date
        date_filter = tmp_data_values.notnull()
        date_dtype_values[date_filter] = "date"
        #update error_counter
        error_counter[filter_used] = date_dtype_values 
    
    return error_counter


def check_column_data_type(field, dtypes):   
    """Check that the data types found in a column is appropiate for the heading that it was matched to.
    
    Args:
        field (str): column heading.
        dtypes ([str]): list of dtypes found for a column heading.

    Returns:
        result (boolean), true or false if appropiate dtype found.
        dtype_set ([str]), matching data types found for mapping.
        conversion_dtype (str): the data type the column needs to be converted to.
    """

    dtypes = [(i[0]) for i in dtypes]
    dtype_set = set()
    result = False
    if field == "country":
        country_list = ['iso2', 'iso3', "country_name"]
        dtype_set = set(dtypes) & set(country_list)
        result = bool(dtype_set)   
       
        if not result:
            dtype_set = dtypes[0]
        else:
            indexes = []
            dtype_set = list(dtype_set)
            
            for i in range(len(dtype_set)):#looking for furthest forward data type found that is compatiable
                indexes.append(int(dtypes.index(dtype_set[i])))
            
            indexes.sort()
            dtype_set = dtypes[indexes[0]]#pointless??
                
        return result, dtype_set, "iso2"
    
    elif field == "measure_value":
        if "num" in dtypes:
            return True, "num" , "num"
        else:
            return False, dtypes[0], "num"
    
    elif field == "date_value":
        if "date" in dtypes:
            ###Future: include format of date
            return True, "date" , "date"
        else:
            return False, dtypes[0] , "date"
    else:
        return True, "str", "str" 


#use validation error lines to get bad data, would optimise 
def correct_data(df_data, correction_data, error_data):#correction_data ["country_name, iso2, iso3 etc"]
    """Corrects data for each column according to correction_data.
    
    Args:
        df_data (Dataframe): dataframe of CSV file.
        correction_mappings ({str:(str,str)}): the conversion needed for each file heading.
        error_data ({str:[str]}): error data for each column.

    Returns: 
        new_df (Dataframe): the converted dataframe.
    """

    value = {}
    _, dicts = get_dictionaries()
    f = (lambda x: str(unicodedata.normalize('NFKD', unicode(x)).lower().encode('ascii','ignore')).strip())

    print("Correction data")
    print(correction_data)

    for key in correction_data:
        not_null_filter = df_data[key].notnull()
        numeric_filter = pd.to_numeric(df_data[key][not_null_filter], errors='coerce').notnull()
        
        ###Country
        if correction_data[key][1] == "iso2":
            print("Country Check")
            filter_used = not_null_filter & (~numeric_filter) & (error_data[key][error_data[key] == correction_data[key][0]])
            df_data[key] = df_data[key][filter_used].apply(f)               
            df_data[key] = df_data[key][filter_used].map(dicts)
        elif correction_data[key][1] == "date":
            print("###############")
            print("Key")
            print(key)
            print(correction_data[key][1])

            ####Numeric check
            filter_applied1 = ((not_null_filter) & (numeric_filter) & (error_data[key][error_data[key] == correction_data[key][0]]))
            df_data[key][filter_applied1] = pd.to_datetime(df_data[key][filter_applied1].astype('str')).dt.year

            ###String check
            filter_applied2 = ((not_null_filter) & (~numeric_filter)) & (error_data[key][error_data[key] == correction_data[key][0]])
            df_data[key][filter_applied2] = pd.to_datetime(df_data[key][filter_applied2]).dt.year

            df_data[key][~(filter_applied1 | filter_applied2)] = np.NaN
        #Applying filter to entire column, example indicator category might be  have numbers 
        elif correction_data[key][1] == "str":
            filter_applied = not_null_filter & (~numeric_filter)
            df_data[key] = df_data[key].apply(f)
        else:#numeric
            filter_applied = not_null_filter & (~numeric_filter)
            df_data[key][filter_applied]  = np.NaN

    return df_data


def lookForError(f, default, x):
    try:
        value = f(x)
    except Exception:
        value = default
    return default

def convert_df(mappings,relationship_dict, left_over_dict, df_data, dtypes_dict, empty_unit_measure_value):
    """Remaps dataframe based on relationship between columns and data model.
    
    Args:
        mappings ({str:[str]}): the users chosen mappings for a file column.
        relationship_dict ({str: [str]}): section of the data model mapped to a file heading.
        left_over_dict_dict ({str: [str]}): section of the data model mapped to the file column values.
        df_data (Dataframe): dataframe of CSV file.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        empty_unit_measure_value (str): value to use if unit of measure has not be mapped.

    Returns: 
        new_df (Dataframe): newly formatted dataframe.
    """

    print("Converting DF")
    print(df_data)
    if not empty_unit_measure_value:
        empty_unit_measure_value = {}

    columns = []
    ###Get columns not in relationship dict
    for col in df_data.columns: 
        temp = str(col)
        col = str(col) 
        if (temp in relationship_dict):
            if not relationship_dict[temp] in columns or not left_over_dict[temp] in columns:
                columns.append(str(relationship_dict[temp]))
                columns.append(str(left_over_dict[temp]))
        else: 
            columns.append(col)

    columns.append('unit_of_measure')
    columns = list(set(columns))#filter duplicates
    columns_set = list(set(list(columns)) & set(list(df_data.columns)))
    
    for col in relationship_dict:
        if relationship_dict[col] == "date_value":
            dtypes_dict[relationship_dict[col]] = [['date', "100%"]]
        else:
            dtypes_dict[relationship_dict[col]] = [['str', "100%"]]

        dtypes_dict[left_over_dict[col]] = [['num', '100%']]

    new_df = pd.DataFrame(columns=df_data.columns)

    for col in relationship_dict:
        tmp_df = df_data.copy(deep=True)    
        
        #if more than one relationship ie multiple subgroupd and relationships
        if col in mappings['indicator_category'] and len(mappings['indicator_category']) > 1:
            tmp_df[relationship_dict[col]] = tmp_df[relationship_dict[col]] + "|" + (col)
            tmp_df[left_over_dict[col]] = tmp_df[col]
            
        else:#normal case
            tmp_df[relationship_dict[col]] = col
            tmp_df[left_over_dict[col]] = tmp_df[col]
        
        if col in empty_unit_measure_value:
            tmp_df['unit_of_measure'] = empty_unit_measure_value[col]
        print("Temp DF")
        print(len(tmp_df.columns))
        print(tmp_df)
        print("New DF")
        print(len(new_df.columns))
        print(new_df)
        new_df = new_df.append(tmp_df)
    
    print(len(df_data[df_data.columns[0]]))
    print(len(new_df[new_df.columns[0]]))
    
    return new_df#filter by columns needed

def check_file_type(file_name):
    name = file_name.lower()
    if name.endswith('.csv'):
        return True ,{'file_type':'csv', 'success':1}
    elif name.endswith('.xlsx'):
        return False, {'file_type':'xlsx', 'success':0, 'error': "Cannot map xlsx files"}
    elif name.endswith('.json'):
        return False, {'file_type':'json', 'success':0, 'error': "Cannot map json files"}
    else:
        return False, {'file_type':'Unrecognised format', 'success':0, 'error': "Don't recognise file type"}#.txt format??

def check_file_formatting(file_loc):
    try:
        df_data = pd.read_csv(file_loc)
    except Exception as e:
        return False, {'success':0, "error":"Couldn't read file, check start of file for text, for malformed columns and  for gaps in data."}
    #check column names if unammed give back false
    for key in df_data.columns:
        if 'Unnamed' in key:
            return False, {'success':0, "error":"Cannot validate, unnamed columns in data set or unessecary text at start of file."}
        else:
            nan_indexes = pd.isnull(df_data)
            #for col in df_data.ix[:,0]:

    resulting_indexes = nan_indexes.apply(lambda x: min(x) == max(x) and min(x) == True, 1)
    result = len(resulting_indexes[resulting_indexes == True]) > 0
    if result:
        return False, {'success':0, "error":"Files has blank lines or text at end of the file."}#return line number of blank lines?
    return True, {"success":1}
    #check end of file if there is empty line and the df_data lenght is longer than this line then error#
    #get columns with the least amount of empty values 
    #check which has the least amount


def get_line_index(line_records, line_no):
    i = 0
    for line in line_records:
        if line["Item"] == line_no:
            return i
        else:
            i += 1
    return -1

