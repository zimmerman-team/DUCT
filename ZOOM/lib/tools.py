from geodata.models import Country, CountryAltName
from indicator.models import IndicatorDatapoint
from lib.common import get_dictionaries
import dateutil.parser as date_parser
import pandas as pd
import numpy as np
import sys
import os
import requests
import json
import re
import unicodedata
from collections import Counter
from django.test import RequestFactory, Client
from rest_framework.test import APIClient
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
    sys.setdefaultencoding("utf-8")

    dtypes_found = []
    error_counter = column_values.astype("str")
    error_counter[:] = np.NaN
    not_null_filter = column_values.notnull()
    numeric_filter = pd.to_numeric(column_values[not_null_filter], errors="coerce").notnull()

    ###Checking Date###
    error_counter = check_if_date(file_heading, column_values, not_null_filter, numeric_filter, error_counter)

    ###Country Check###
    if(np.sum(error_counter.notnull()) < len(error_counter)):

        try:
            f = (lambda x: str(unicodedata.normalize("NFKD", unicode(x)).lower().encode("ascii","ignore")).strip().replace("_", " "))
            filter_used = not_null_filter & (~numeric_filter)
            tmp_country_values = column_values[filter_used].apply(f)
            tmp_country_values = tmp_country_values.map(dicts)
            #get values that are not null => country
            country_filter = tmp_country_values.notnull()
            error_counter[filter_used] = tmp_country_values[country_filter]
        except Exception:#not pretty!!!
            f2 = (lambda x: str(re.sub(r'[^\x00-\x7F]+',' ', x))) #very slow
            filter_used = not_null_filter & (~numeric_filter)
            tmp_country_values = column_values[filter_used].apply(f2)
            tmp_country_values = tmp_country_values.apply(f)
            tmp_country_values = tmp_country_values.map(dicts)
            #get values that are not null => country
            country_filter = tmp_country_values.notnull()
            error_counter[filter_used] = tmp_country_values[country_filter]
            
    ###Clean up###
    error_counter[~not_null_filter] = "blank"
    
    filter_used = (error_counter.isnull()) & (not_null_filter & (~numeric_filter))
    error_counter[filter_used] ="text"
    
    filter_used = (error_counter.isnull()) & (not_null_filter & numeric_filter)
    error_counter[filter_used] = "numeric"

    dtypes_found = np.unique(error_counter)
    prob_list = get_prob_list(error_counter)
    return prob_list, error_counter
    
def check_if_date(file_heading, column_values, not_null_filter, numeric_filter, error_counter):
    """Check if column values could be a date.
    
    Args:
        file_heading (str): heading of the file.
        column_values (Series): values related to a column.
        not_null_filter (np[boolean]): filters for non-null values.
        numeric_filter (np[boolean]): filters for numeric values.
        error_counter ([int]): error data, a list that will contain all data types for column_values.

    Returns: 
        result (boolean): result of check.
        error_counter ([int]): error data, a list that will contain all data types for column_values. 

    """

    # assuming time or date will have appropiate heading, perhaps a bad assumption
    result = "time" in file_heading.lower() or "date" in file_heading.lower() or "year" in file_heading.lower() or "period" in file_heading.lower()
    if result:
        filters = [((not_null_filter) & (numeric_filter)), ((not_null_filter) & (~numeric_filter))] 
        filter_types = ["int", "string"]
        for i in range(len(filters)):
            filter_applied = filters[i]
            values = column_values[filter_applied]
            if filter_types[i] == "int":
               values = values.astype(int)
            tmp_data_values = pd.to_datetime(values.astype("str"), errors = "coerce")
            date_dtype_values = error_counter[filter_applied]
        
            #get values that are not null => date
            date_filter = tmp_data_values.notnull()
            date_dtype_values[date_filter] = "date"
            #update error_counter
            error_counter[filter_applied] = date_dtype_values 

    return error_counter


def get_prob_list(error_counter):
    """Gets the probability listing of all data-types found"""
    prob_list = []
    normalisation = float(len(error_counter))
    for heading, count in Counter(error_counter).most_common():
        prob_list.append((heading, "{0:.0f}%".format(float(count)/normalisation * 100)))
    return prob_list


def update_cell_type(value, error_counter, line_no, file_heading):
    """Used when checking just one cell so no vectorisation"""
    reload(sys)
    sys.setdefaultencoding("utf-8")
    date_check_f = (lambda x: "time" in x.lower() or "date" in x.lower() or "year" in x.lower() or "period" in x.lower())
    date_f = (lambda x: date_parser.parse(str(x)))
    
    try:
        result = "".join(str(value).split()) == "" 
        if result:
            dtype = "blank"
    except Exception:
        result = False

    if not value:
        dtype = "blank"
    else:
        ###Integer
        try:
            tmp = int(value)
            ##Checking Date###
            result = date_check_f(file_heading)
            if result:
                try:
                    tmp = date_f(tmp)
                    dtype = "date"
                except Exception:
                    result = False

            if not result:
                dtype = "numeric"
        ###String
        except Exception:
            ###Checking Date###
            f = (lambda x: str(unicodedata.normalize("NFKD", unicode(x)).lower().encode("ascii","ignore")).strip().replace("_", " "))
            value = f(value)
            result = date_check_f(file_heading)
            if result:
                try:
                    value = date_f(value)
                    dtype = "date"
                except Exception:
                    result = False
            
            ###Country Check###
            if(not result):
                value = f(value)
                result, dtype = check_if_cell_country(value) 

            if(not result):
                dtype ="text"
    
    error_counter[line_no] = dtype   
    prob_list = get_prob_list(error_counter)
    return prob_list, error_counter


def check_if_cell_country(value):
    """Checks if value is a country"""
    result = Country.objects.filter(code__iexact=value).exists()
    if result:
        return result,"country(iso2)"

    result = Country.objects.filter(iso3__iexact=value).exists()
    if result:
        return result, "country(iso3)"

    result = Country.objects.filter(name__iexact=value).exists()
    if result:
        return result, "country(name)"

    result = CountryAltName.objects.filter(name__iexact=value).exists()
    if result:
        return result, "country(name)"

    return False, ""


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
        country_list = ["country(iso2)", "country(iso3)", "country(name)"]
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
                
        return result, dtype_set,"country(iso2)"
    
    elif field == "measure_value":
        if "numeric" in dtypes:
            return True, "numeric" , "numeric"
        elif"text" in dtypes:
            return True,"text" , "numeric"
        else:
            return False, dtypes[0], "numeric"
    
    elif field == "date_value":
        if "date" in dtypes:
            ###Future: include format of date
            return True, "date" , "date"
        else:
            return False, dtypes[0] , "date"
    else:
        return True,"text","text" 


#use validation error lines to get bad data, would optimise 
def correct_data(df_data, correction_data, error_data, index_order):#correction_data ["country_name, iso2, iso3 etc"]
    """Corrects data for each column according to correction_data.
    
    Args:
        df_data (Dataframe): dataframe of CSV file.
        correction_mappings ({str:(str,str)}): the conversion needed for each file heading.
        error_data ({str:[str]}): error data for each column.
        index_order ({str: str}): contains data points as headings and columns as values.

    Returns: 
        new_df (Dataframe): the converted dataframe.
    """
    
    value = {}
    _, dicts = get_dictionaries()
    f = (lambda x: str(unicodedata.normalize("NFKD", unicode(x)).lower().encode("ascii","ignore")).strip().replace("_", " "))

    for key in correction_data:
        not_null_filter = df_data[key].notnull()
        numeric_filter = pd.to_numeric(df_data[key][not_null_filter], errors="coerce").notnull()
        
        ###Country
        if correction_data[key][1] =="country(iso2)":
            filter_used = not_null_filter & (~numeric_filter) & (error_data[key][error_data[key] == correction_data[key][0]])
            df_data[key] = df_data[key][filter_used].apply(f)               
            df_data[key] = df_data[key][filter_used].map(dicts)
        elif correction_data[key][1] == "date":
            ####Numeric check
            filter_applied1 = ((not_null_filter) & (numeric_filter) & (error_data[key][error_data[key] == correction_data[key][0]]))
            df_data[key][filter_applied1] = pd.to_datetime(df_data[key][filter_applied1].astype("int").astype("str")).dt.year

            ###String check
            filter_applied2 = ((not_null_filter) & (~numeric_filter)) & (error_data[key][error_data[key] == correction_data[key][0]])
            df_data[key][filter_applied2] = pd.to_datetime(df_data[key][filter_applied2]).dt.year

            df_data[key][~(filter_applied1 | filter_applied2)] = np.NaN
        #Applying filter to entire column, example indicator category might be  have numbers 
        elif correction_data[key][1] =="text":
            filter_applied = not_null_filter & (~numeric_filter)
            df_data[key] = df_data[key].apply(f)
        else:#numeric
            if correction_data[key][0] =="text":
                if index_order["measure_value"] == key:
                    #get inidicator category add and group accordingly
                    df_data[index_order["indicator_filter"]] = (df_data[index_order["indicator_filter"]] + "|" + index_order["measure_value"] + ": "
                                                                + df_data[index_order["measure_value"]])
                    str_data = pd.DataFrame({index_order["measure_value"] + "temp" : df_data.groupby([index_order["indicator"], index_order["indicator_filter"], 
                                                                            index_order["country"], index_order["date_value"], index_order["unit_of_measure"], 
                                                                            index_order["measure_value"]])[index_order["measure_value"]
                                                                            ].count()}).reset_index()
                    #Cause we are grouping by sources and other don't make sense
                    if "source" in index_order:
                        str_data[index_order["source"]] = ""
                    if "other" in index_order:
                        str_data[index_order["other"]] = ""
                    str_data[index_order["measure_value"]] = str_data[index_order["measure_value"] + "temp"] 
                    df_data = str_data.drop(index_order["measure_value"] + "temp", 1)
            else:
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
        relationship_dict ({str: [str]}): section of the data model mapped to a file column heading.
        left_over_dict ({str: [str]}): section of the data model mapped to the file column values.
        df_data (Dataframe): dataframe of CSV file.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        empty_unit_measure_value (str): value to use if unit of measure has not be mapped.

    Returns: 
        new_df (Dataframe): newly formatted dataframe.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        heading_order ([str]): 
    """

    heading_order = []

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

    columns.append("unit_of_measure")
    columns = list(set(columns))#filter duplicates
    columns_set = list(set(list(columns)) & set(list(df_data.columns)))
    
    #for col in relationship_dict:
    #    dtypes_dict[left_over_dict[col]] = []
    #print("relationship_dict ", relationship_dict);

    for col in relationship_dict:
        if relationship_dict[col] == "date_value":
            dtypes_dict[relationship_dict[col]] = [("date", "100%")]
        else:
            dtypes_dict[relationship_dict[col]] = [("text", "100%")]

        ###################Need to combine datatypes for each
        dtypes_dict[left_over_dict[col]] = dtypes_dict[col]

    new_df = pd.DataFrame(columns=df_data.columns)

    for col in relationship_dict:
        heading_order.append(col)
        #print('#############################')
        #print("mappings ", mappings["indicator_filter"])
        #print(col)
    
        tmp_df = df_data.copy(deep=True)    
        
        #if more than one relationship is multiple subgroupd and relationships
        if col in mappings["indicator_filter"] and len(mappings["indicator_filter"]) > 1:
            """print("Ind Cat " + col);
            print(tmp_df[relationship_dict[col]] + "|" + (col))
            print(tmp_df[col])
            print("------------------")"""
            tmp_df[relationship_dict[col]] = tmp_df[relationship_dict[col]] + "|" + (col)
            tmp_df[left_over_dict[col]] = tmp_df[col]
            if left_over_dict[col] == "measure_value":
                tmp_df["heading_filter"] = tmp_df['heading_filter'] + "|" + "Measure Value"
            else:
                tmp_df["heading_filter"] = tmp_df['heading_filter'] + "|" + col.replace("_", " ").lower().title()
        else:#normal case
            if col in mappings["indicator_filter"]:
                if left_over_dict[col] == "measure_value":
                    tmp_df["heading_filter"] = "Measure Value"
                else:
                    tmp_df["heading_filter"] =  col.replace("_", " ").lower().title()  
            
            tmp_df[relationship_dict[col]] = col
            tmp_df[left_over_dict[col]] = tmp_df[col]
        
        if col in empty_unit_measure_value:
            tmp_df["unit_of_measure"] = empty_unit_measure_value[col]
        new_df = new_df.append(tmp_df)

    #reset mappings to indicator category and measure value ##check if this is needed.
    mappings[relationship_dict[col]] = relationship_dict[col]
    mappings[left_over_dict[col]] = left_over_dict[col] 
    
    #print(new_df.reset_index()['indicator_filter']);
    return new_df.reset_index(), dtypes_dict, mappings #filter by columns needed

def check_file_type(file_name):
    name = file_name.lower()
    if name.endswith(".csv"):
        return True ,{"file_type":"csv", "success":1}
    elif name.endswith(".xlsx"):
        return False, {"file_type":"xlsx", "success":0, "error": "Cannot map xlsx files"}
    elif name.endswith(".json"):
        return False, {"file_type":"json", "success":0, "error": "Cannot map json files"}
    else:
        return False, {"file_type":"Unrecognised format", "success":0, "error": "Don't recognise file type"}#.txt format??

def check_file_formatting(file_loc):
    try:
        df_data = pd.read_csv(file_loc)
    except Exception as e:
        return False, {"success":0, "error":"Couldn't read file, check start of file for text, for malformed columns and  for gaps in data."}
    #check column names if unammed give back false
    for key in df_data.columns:
        if "Unnamed" in key:
            return False, {"success":0, "error":"Cannot validate, unnamed columns in data set or unessecary text at start of file."}
        else:
            nan_indexes = pd.isnull(df_data)
            #for col in df_data.ix[:,0]:

    resulting_indexes = nan_indexes.apply(lambda x: min(x) == max(x) and min(x) == True, 1)
    result = len(resulting_indexes[resulting_indexes == True]) > 0
    if result:
        return False, {"success":0, "error":"Files has blank lines or text at end of the file."}#return line number of blank lines?
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

#from file_upload.models import File

URL="http://127.0.0.1:8000/api/"
WB = "World_Bank"
CRS = "CRS"
DEFAULT_INDICATOR_COLUMN = "indicator" 
file_dict = {
                WB:{
                        "tag":WB, 
                        "source":WB,
                        "description": "Indicator data from WB (upload done through automation).",
                        "file_tags": ["WB"],
                        "mapping":{
                            'indicator': [DEFAULT_INDICATOR_COLUMN], 
                            'unit_of_measure': [],
                            'relationship': {
                                            '2003': 'date_value',  
                                            '1997': 'date_value', 
                                            '1988': 'date_value', 
                                            '1989': 'date_value', 
                                            '1986': 'date_value', 
                                            '1987': 'date_value', 
                                            '1984': 'date_value',
                                            '1985': 'date_value', 
                                            '1968': 'date_value', 
                                            '1969': 'date_value', 
                                            '1980': 'date_value', 
                                            '1981': 'date_value', 
                                            '1964': 'date_value', 
                                            '1965': 'date_value', 
                                            '1966': 'date_value', 
                                            '1967': 'date_value', 
                                            '1960': 'date_value',
                                            '1961': 'date_value', 
                                            '1962': 'date_value',
                                            '1963': 'date_value',
                                            '1996': 'date_value', 
                                            '2014': 'date_value', 
                                            '2017': 'date_value', 
                                            '2016': 'date_value', 
                                            '2011': 'date_value', 
                                            '2010': 'date_value',
                                            '2013': 'date_value', 
                                            '2012': 'date_value', 
                                            '2005': 'date_value', 
                                            '2015': 'date_value', 
                                            '1982': 'date_value', 
                                            '1983': 'date_value', 
                                            '1991': 'date_value', 
                                            '1990': 'date_value', 
                                            '1993': 'date_value', 
                                            '1992': 'date_value', 
                                            '1995': 'date_value', 
                                            '1994': 'date_value', 
                                            '1979': 'date_value', 
                                            '1978': 'date_value', 
                                            '1977': 'date_value', 
                                            '1976': 'date_value', 
                                            '1975': 'date_value', 
                                            '1974': 'date_value', 
                                            '1973': 'date_value', 
                                            '1972': 'date_value', 
                                            '1971': 'date_value', 
                                            '1970': 'date_value', 
                                            '2002': 'date_value', 
                                            '1999': 'date_value',
                                            '2000': 'date_value', 
                                            '2001': 'date_value', 
                                            '2006': 'date_value', 
                                            '2007': 'date_value', 
                                            '2004': 'date_value', 
                                            '1998': 'date_value', 
                                            '2008': 'date_value', 
                                            '2009': 'date_value'
                            }, 
                            'left_over': {  '2003': 'measure_value', '1997': 'measure_value', '1988': 'measure_value', 
                                            '1989': 'measure_value', '1986': 'measure_value', '1987': 'measure_value', 
                                            '1984': 'measure_value', '1985': 'measure_value', '1968': 'measure_value',
                                            '1969': 'measure_value', '1980': 'measure_value', '1981': 'measure_value',
                                            '1964': 'measure_value', '1965': 'measure_value', '1966': 'measure_value', 
                                            '1967': 'measure_value', '1960': 'measure_value', '1961': 'measure_value',
                                            '1962': 'measure_value', '1963': 'measure_value', '1996': 'measure_value',
                                            '2014': 'measure_value', '2017': 'measure_value', '2016': 'measure_value',
                                            '2011': 'measure_value', '2010': 'measure_value', '2013': 'measure_value',
                                            '2012': 'measure_value', '2005': 'measure_value', '2015': 'measure_value',
                                            '1982': 'measure_value', '1983': 'measure_value', '1991': 'measure_value',
                                            '1990': 'measure_value', '1993': 'measure_value', '1992': 'measure_value',
                                            '1995': 'measure_value', '1994': 'measure_value', '1979': 'measure_value', 
                                            '1978': 'measure_value', '1977': 'measure_value', '1976': 'measure_value', 
                                            '1975': 'measure_value', '1974': 'measure_value', '1973': 'measure_value', 
                                            '1972': 'measure_value', '1971': 'measure_value', '1970': 'measure_value', 
                                            '2002': 'measure_value', '1999': 'measure_value', '2000': 'measure_value', 
                                            '2001': 'measure_value', '2006': 'measure_value', '2007': 'measure_value', 
                                            '2004': 'measure_value', '1998': 'measure_value', '2008': 'measure_value', 
                                            '2009': 'measure_value'}, 
                            'country': ['Country Code'], 
                            'empty_indicator': 'test', 
                            'measure_value': [  '1960', '1961', '1962', '1963', '1964', '1965', '1966', 
                                                '1967', '1968', '1969', '1970', '1971', '1972', '1973', 
                                                '1974', '1975', '1976', '1977', '1978', '1979', '1980', 
                                                '1981', '1982', '1983', '1984', '1985', '1986', '1987', 
                                                '1988', '1989', '1990', '1992', '1991', '1993', '1994',
                                                '1995', '1996', '1997', '1998', '1999', '2000', '2001', 
                                                '2002', '2003', '2004', '2005', '2006', '2007', '2008', 
                                                '2009', '2010', '2011', '2012', '2013', '2014', '2015',
                                                '2016', '2017'], 
                            'date_value': [     '1960', '1961', '1962',
                                                '1963', '1964', '1965', '1966', '1967', '1968', '1969', 
                                                '1970', '1971', '1972', '1973', '1974', '1975', '1976', 
                                                '1977', '1978', '1979', '1980', '1981', '1982', '1983', 
                                                '1984', '1985', '1986', '1987', '1988', '1989', '1990', 
                                                '1991', '1992', '1993', '1994', '1995', '1996', '1997',
                                                '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                                                '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                                                '2012', '2013', '2014', '2015', '2016', '2017'], 
                            'source': [], 
                            'other': [], 
                            'indicator_filter': ['Indicator Name'], 
                            'empty_unit_of_measure': {'2003': 'Number', '1997': 'Number', '1988': 'Number', '1989': 'Number', 
                                                      '1986': 'Number', '1987': 'Number', '1984': 'Number', '1985': 'Number', 
                                                      '1968': 'Number', '1969': 'Number', '1980': 'Number', '1981': 'Number', 
                                                      '1964': 'Number', '1965': 'Number', '1966': 'Number', '1967': 'Number', 
                                                      '1960': 'Number', '1961': 'Number', '1962': 'Number', '1963': 'Number', 
                                                      '1996': 'Number', '2014': 'Number', '2017': 'Number', '2016': 'Number', 
                                                      '2011': 'Number', '2010': 'Number', '2013': 'Number', '2012': 'Number', 
                                                      '2005': 'Number', '2015': 'Number', '1982': 'Number', '1983': 'Number', 
                                                      '1991': 'Number', '1990': 'Number', '1993': 'Number', '1992': 'Number', 
                                                      '1995': 'Number', '1994': 'Number', '1979': 'Number', '1978': 'Number', 
                                                      '1977': 'Number', '1976': 'Number', '1975': 'Number', '1974': 'Number', 
                                                      '1973': 'Number', '1972': 'Number', '1971': 'Number', '1970': 'Number', 
                                                      '2002': 'Number', '1999': 'Number', '2000': 'Number', '2001': 'Number', 
                                                      '2006': 'Number', '2007': 'Number', '2004': 'Number', '1998': 'Number', 
                                                      '2008': 'Number', '2009': 'Number'}
                        },
                        "input_path":"../scripts/formatters/" + WB + "/input/", 
                        "output_path":"../scripts/formatters/" + WB + "/output/",
                        "conversion":"../scripts/formatters/" + WB + "/",
                        "columns":[
                                DEFAULT_INDICATOR_COLUMN,
                                "Indicator Name",    
                                "Country Code",
                                "1960",
                                "1961",
                                "1962",
                                "1963",
                                "1964",
                                "1965",
                                "1966",
                                "1967",
                                "1968",
                                "1969",
                                "1970",
                                "1971",
                                "1972",
                                "1973",
                                "1974",
                                "1975",
                                "1976",
                                "1977",
                                "1978",
                                "1979",
                                "1980",
                                "1981",
                                "1982",
                                "1983",
                                "1984",
                                "1985",
                                "1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996",
                                "1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007",
                                "2008","2009","2010","2011","2012","2013","2014","2015","2016","2017"
                        ]
                },    
                CRS:{   
                        "tag":CRS, 
                        "source":CRS,
                        "description": "Aggregated CRS from OECD (upload done through automation).",
                        "file_tags": ["Finance", "CRS"],
                        "mapping":{
                                    'indicator': ['Flow Name'], 
                                    'unit_of_measure': [],
                                    'relationship': {
                                                    'Commitments Defl': 'indicator_filter', 
                                                    'Disbursements': 'indicator_filter', 
                                                    'Disbursements Defl': 'indicator_filter',
                                                    'Commitments': 'indicator_filter'}, 
                                    'left_over': {
                                                    'Commitments Defl': 'measure_value', 
                                                    'Disbursements': 'measure_value',
                                                    'Disbursements Defl': 'measure_value', 
                                                    'Commitments': 'measure_value'}, 
                                    'country': ['Recipient'], 
                                    'measure_value': ['Currency', 'Commitments', 'Disbursements', 'Commitments Defl', 'Disbursements Defl'], 
                                    'date_value': ['Year'], 
                                    'source': [], 
                                    'other': [], 
                                    'indicator_filter': ['Sector', 'Aid Type', 'Income Group', 'Purpose', 'Donor', 'Finance Type', 'Commitments', 'Disbursements', 'Commitments Defl', 'Disbursements Defl'], 
                                    'empty_unit_of_measure': {'Currency': 'Number', 'Disbursements': 'Number', 'Disbursements Defl': 'Number', 'Commitments': 'Number', 'Commitments Defl': 'Number'}
                        }, 
                        "input_path":"../scripts/formatters/" + CRS + "/input/", 
                        "output_path":"../scripts/formatters/" + CRS + "/output/",
                        "conversion":"../scripts/formatters/" + CRS + "/",
                        "columns":[
                            "Year",
                            "DonorName",    
                            "RecipientName",
                            "IncomegroupName",
                            "FlowName",
                            "Finance_t",
                            "Aid_t",
                            "usd_commitment",
                            "usd_disbursement", 
                            "usd_commitment_defl",
                            "usd_disbursement_defl",    
                            "CurrencyCode",
                            "PurposeName",
                            "SectorName"
                        ],
                        "nice_name":{
                            "Year": "Year",
                            "DonorName": "Donor",   
                            "RecipientName": "Recipient",
                            "IncomegroupName": "Income Group",
                            "FlowName": "Flow Name",
                            "Finance_t": "Finance Type",
                            "Aid_t": "Aid Type",
                            "usd_commitment": "Commitments",
                            "usd_disbursement": "Disbursements",    
                            "usd_commitment_defl": "Commitments Defl",
                            "usd_disbursement_defl": "Disbursements Defl",  
                            "CurrencyCode": "Currency",
                            "PurposeName": "Purpose",
                            "SectorName": "Sector"
                        },
                        "measure_value":[ "Commitments", "Disbursements", "Commitments Defl", "Disbursements Defl"]
                    }
            }

file_list = [WB, CRS]
character_sep = {WB: ",", CRS: "|"}

def add_external_data():
    global character_sep
    checked = False
    file_choice = CRS;#"CRS" #temp
    #file_choice = ""
    """print("Enter one of the following: ", file_list)
                print("e for escape")
                while(not checked):
                    #try:
                    file_choice = input("Enter data desired from above:")
                    if(file_choice in file_list):
                        checked = True
                    elif(file_choice == "e"):
                        sys.exit()
                    #except EOFError:
                    #    error = ""
    """

    convert_data(file_choice)
    if(file_choice == CRS):
        flatten_data(file_choice)
    checkIfFilesTooBig(file_choice)
    start_mapping(file_choice)

def start_mapping(file_choice):
    global file_list, file_dict
    path = file_dict[file_choice]["output_path"]
    file_list = os.listdir(path)
    counter = 0
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    for file_name in file_list:
        
        headers = {'Content-type': 'multipart/form-data'}
        with open(path + file_name, 'rb') as fp:
                res_file_upload = c.post(
                        URL + 'file/?format=json', 
                        {
                            'file':fp,
                            'title': file_name, 
                            'description': (file_name + " " + file_dict[file_choice]["description"]), 
                            'file_name': file_name
                        })
        print("Upload file: ", res_file_upload)

        headers = {'content-type': 'application/json'}
        patch_data = {
            'title': file_name, 
            'description': file_name + " " + file_dict[file_choice]["description"], 
            'file_name': file_name,
            "tags": file_dict[file_choice]["file_tags"], 
            "data_source": file_choice,
            "authorised": 1,
            "status": 1
        }

        file_id = res_file_upload.json()['id']
        print('file_id ', file_id)
        res = requests.patch(
                    URL + 'file/{}/?format=json'.format(file_id), 
                    headers=headers,
                    data=(json.dumps(patch_data))
                )#""""""
        print("Update file: ", res)

        res = c.post(
                URL + 'validate/?format=json', 
                {
                    "file_id": file_id
                },  format='json')
        print("Validation: ", res)
        
        res = c.post(
                URL + 'manual-mapper/?format=json', 
                {
                    "file_id": file_id,
                    "dict": file_dict[file_choice]['mapping']
                },  format='json')        
        print("Mapping: ", res)
        

        res = c.post(
                URL + 'file/update_status/?format=json', 
                {
                    "file_id": file_id,
                    "status": 5
                })        
        print("Status: ", res.json())

def checkIfFilesTooBig(file_choice):
    global file_list, file_dict
    SPLIT_SIZE = 5500000
    path = file_dict[file_choice]["output_path"]
    file_list = os.listdir(path)
    counter = 0

    for file_name in file_list:
        size = os.path.getsize(path + file_name)
        if(size > SPLIT_SIZE):#over 5.5mb split
            data = pd.read_csv(path + file_name, sep=character_sep[file_choice])
            print("Size of file: ", size)
            split_range = math.ceil(size/SPLIT_SIZE)
            data_split = np.array_split(data, split_range)
            for i in range(split_range):
                data_split[i].to_csv(file_dict[file_choice]["output_path"] + file_name[:-4]+ "(" + i + ")" + ".csv", sep=',', index = False)  
            os.remove(path + file_name)

            print("Split file: ", split_range )

"""
Created on Mon Nov 20 09:42:29 2017
@author: marco
This script format crs data: 
    The original file uses "|" instead of ","
"""
def convert_data(file_choice):
    global character_sep, file_dict
    file_list = os.listdir(file_dict[file_choice]["input_path"])
    counter = 0
    #get files in folder
    print("Begining Conversion")
    
    for file_name in file_list:
        data = pd.read_csv(file_dict[file_choice]["input_path"] + file_name, sep=character_sep[file_choice])
        if file_choice == WB:
            data[DEFAULT_INDICATOR_COLUMN] = data[data.columns[0]]
            data[DEFAULT_INDICATOR_COLUMN] = file_name[:-4]
            data = data.iloc[4:]#remove first 4 rows
        data = data[file_dict[file_choice]["columns"]]
        if "nice_name" in file_dict[file_choice]:
            data.rename(columns=file_dict[file_choice]["nice_name"], inplace=True)
        ##check column width and size an split accoringly
        data.to_csv(file_dict[file_choice]["output_path"] + file_name[:-4]+".csv", sep=',', index = False)
        sys.stdout.write("\r%d%%" % ((counter/len(file_list)) * 100) )

    sys.stdout.flush()
    #print("All files converted")

def flatten_data(file_choice):
    global character_sep, file_dict
    file_list = os.listdir(file_dict[file_choice]["output_path"])
    measure_values = file_dict[file_choice]["measure_value"]
    counter = 0
    columns = list(file_dict[file_choice]["nice_name"].values())
    columns = list(set(columns) - set(measure_values))
    aid_t_conv = pd.read_csv(file_dict[file_choice]["conversion"] + "aid_types.csv")
    aid_t_conv = pd.Series(aid_t_conv.Name.values,index=aid_t_conv.Code).to_dict()
    currency_t_conv = pd.read_csv(file_dict[file_choice]["conversion"] + "currency_types.csv")
    currency_t_conv = pd.Series(currency_t_conv.Name.values,index=currency_t_conv.Code).to_dict()
    finance_t_conv = pd.read_csv(file_dict[file_choice]["conversion"] + "finance_types.csv")
    finance_t_conv = pd.Series(finance_t_conv.Name.values,index=finance_t_conv.Code).to_dict()

    print("Begining Conversion")
    
    for file_name in file_list:
        data = pd.read_csv(file_dict[file_choice]["output_path"] + file_name)
        data.fillna(value=0, inplace=True)
        data["Aid Type"] = data["Aid Type"].map(aid_t_conv)
        data["Finance Type"] = data["Finance Type"].map(finance_t_conv)
        data["Currency"] = data["Currency"].map(currency_t_conv)
        series_list = []

        for measure_value in measure_values:
            tmp = data.groupby(columns)[measure_value].sum()
            series_list.append(tmp)
        data = pd.concat(series_list, axis=1).reset_index()
        data.to_csv(file_dict[file_choice]["output_path"] + file_name[:-4]+".csv", sep=',', index = False)
        sys.stdout.write("\r %d%%" % ((counter/len(file_list)) * 100) )

    sys.stdout.flush()

def mapping(mapping_dict, file):
    print("Begining Mapping ", file)

    print("Finished Mapping ", file)

if __name__ == "__main__":
    main()
