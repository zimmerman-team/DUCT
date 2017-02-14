import strict_rfc3339
import datetime
from functools import wraps  # use this to preserve function signatures and docstrings
from geodata.models import Country
from indicator.models import IndicatorDatapoint
from collections import Counter
from dateutil.parser import parse
import pandas as pd
import numpy as np
#import complier

def ignore_errors(f):
    @wraps(f)
    def ignore(json_data, ignore_errors=False):
        if ignore_errors:
            try:
                return f(json_data)
            except (KeyError, TypeError, IndexError, AttributeError):
                return {}
        else:
            return f(json_data)
    return ignore

def to_list(item):
    if isinstance(item, list):
        return item
    return [item]

def get_no_exception(item, key, fallback):
    try:
        return item.get(key, fallback)
    except AttributeError:
        return fallback

def update_docs(document_parent, counter):
    count = 0
    documents = document_parent.get('documents', [])
    for document in documents:
        count += 1
        doc_type = document.get("documentType")
        if doc_type:
            counter.update([doc_type])
    return count


def datetime_or_date(instance):
    result = strict_rfc3339.validate_rfc3339(instance)
    if result:
        return result
    return datetime.datetime.strptime(instance, "%Y-%m-%d")

#serach for columns that map together, look for specific vlaues such as time
#assume whole column is uploaded, the full length
def identify_col_dtype(column_values, file_heading, dicts,sample=None): #only takle a sample of three value and serach for data type
    #   if sample != "None":
        #provide sample data with indexes
        #df_file[heading].sample(n=sample_amount)

    # take sample here id need be
    #check hxl tag
    #   if so narrow down data types
    #check if numeric or not
    #   if so narrow down possibilities
    #       date, measure value, get unit of measure
    #  
    #if string
    #   check if it can be changed to numeric
    #   check if calculation
    #   check if check country codes, catogorys, indicators, etc
    #
    #column_values = np.array(column_values)
    dtypes_found = []
    prob_list = []
    fields_in_datamodel = []
    prob_threshold = 0.6
    counter = 0
    error_counter = []

    iso2_codes_dict = dicts[0]
    iso3_codes_dict = dicts[1]
    country_names_dict = dicts[2]

    temp = iso2_codes_dict['BG']

    for value in column_values:
        #if string
        if value in iso2_codes_dict:#try:#change to if statements, expections more costly than ifs
            check_dtype = "iso2"
            #check_dtype = iso2_codes_dict[value]#Country.objects.get(code=value)#exists django
            error_counter.append(("iso2",counter))
            dtypes_found.append("iso2")
        else:#except ValueError:#Country.DoesNotExist: # check name
            check_dtype = None
            if value in country_names_dict:#try: 
                check_dtype = "country_name"#country_names_dict[value]#Country.objects.get(name=value)
                error_counter.append(("country_name", counter))
                dtypes_found.append("country_name")
            else:#except ValueError:#Country.DoesNotExist: # check name
                check_dtype = None
                if value in iso3_codes_dict:#try: 
                    check_dtype="iso3"#check_dtype = iso3_codes_dict[value]#Country.objects.get(iso3=value)
                    error_counter.append(("iso3", counter))
                    dtypes_found.append("iso3")
                else:#except ValueError:#Country.DoesNotExist: # check name
                    check_dtype = None
        #check for country codes

        if not check_dtype:
            if "time" in file_heading.lower() or "date" in file_heading.lower():# assuming time or date will have appropiate heading
                try: 
                    check_dtype = parse(str(value))
                    error_counter.append(("date", counter))
                    dtypes_found.append("date")
                except ValueError:
                    dtypes_found.append("possiblly date")
                    error_counter.append(("possiblly date", counter))
                    
                #check if string value is a formula     
                #try convert to number
                #use complier to compler equation # might have to change equation syntax to match python's syntax
            else:
                try:
                    float(value) 
                    check_dtype = "numeric"
                    error_counter.append(("numeric", counter))
                    dtypes_found.append("numeric")
                except ValueError:
                    check_dtype = "str"
                    error_counter.append(("str",counter))
                    dtypes_found.append("str")
        counter += 1
            #else isinstance(value, basestring):
            #    check_dtype = "str"
            #    dtypes_found.append("str")
  
    dtypes_found = (dtypes_found)

    if len(dtypes_found) > 0:
        normalisation = float(len(column_values))
        for heading, count in Counter(dtypes_found).most_common():
            prob_list.append((heading, "{0:.0f}%".format(float(count)/normalisation * 100)))
    else:
        prob_list.append("No data type found with any certainity")
    #probability that we have a matched column, need this has erroneous data types possible, 
    #and nan null etc, can increase probability needed, perhaps based on size of dataset?
    #if highest_found[0][1]/len(column_values) >= prob_threshold:
    #    return highest_found #return datatype and value
    return prob_list, error_counter
    #return "DTNF"#DTNF = Data Type Not Found #might be better to use null


def check_column_data(dtypes, column_data, model_field, file_heading):#No need for this method anymore 
    #has to map to indicator datapoint
    result_list = []
    altered_column = []
    expected_dtypes  = []
    convert_to_type = []
    dtypes = [(i[0]) for i in dtypes]
    if not dtypes or dtypes == "No data type found with any certainity":# for test purposes
        return True #for test purposes

    return check_data_type(model_field, dtypes)
    #if result is False:
    #    return 
    #    #return ("Column '" + model_field + "' expecting the data value to be " + ', '.join(expected_dtypes) + ", instead mapping column '" + file_heading + "'' has data type " + ', '.join(dtypes)), expected_dtypes
    #else:
        #alter date based in data set use dtypes
    #    return "", expected_dtypes  
    

    #check dtypes of column 1 and column 2
    #if different return false
    #identify column against predefined data structure eg iso
    #if heading is clear and data structure for column is known check corresponding column
        #check for incorrect values #iso codes, coutry names
    #if column is a sum change is or highlight it

#returns if data type matches, the type of of attempted map and the type needed for conversion 
#should return field to map to
def check_data_type(field, dtypes):   
    #add time
    dtype_set = set()
    result = False
    if field == "country_id":
        country_list = ['iso2', 'iso3', "country_name"]
        dtype_set = set(dtypes) & set(country_list)
        result = bool(dtype_set)   

        if not result:
            dtype_set = dtypes[0]
        else:
            dtype_set = list(dtype_set)[0]

        if "country_name" == dtype_set:
            dtype_set = "name"
        elif "iso2" == dtype_set:
            dtype_set = "code"
            
        return result, dtype_set, "iso2" #return type found
    
    elif field == "measure_value":
        if "numeric" in dtypes:
            return True, "numeric" , "numeric"#("numeric" in dtypes), ["numeric"]
        else:
            return False, dtypes[0], "str"
    
    elif field == "date_value":
        if "date" in dtypes:#just return this
            return True, "date" , "date"
        else:
            return False, dtypes[0] , "date"
    else:#string
        return True, "str", "str" 

def correct_data(df_data, correction_data):#correction_data ["country_name, iso2, iso3 etc"]
    
    value = {}
    for key in correction_data:
        #decide what format to goive it too #also check date
        if correction_data[key][1] == "iso2":
            model = Country.objects.all()
        #elif date
        #elif measure value etc
            
            for i in range(len(df_data[key])):
                value[correction_data[key][0]] = df_data[key][i] #might not work?
                query_result = model.filter(**value)
                
                if  query_result.count() > 0:
                    model_value = query_result[0].code
                else:
                    model_value = "NA"
                df_data[key][i] = model_value

    return df_data
        #elif correction_data[key][1] == "numeric":
            #model = Country.objects.all()
        #else:

        #for i in range(len(df_data[key])):
        #    value = correction_data[key][0] + "=" + df_data[key][i] #might not work?
        #    value = model.filter(**value)
        #    df[data][i] = value.id
    #if country convert column to iso2
    #if numeric convert to decimal/char
    #if date convert in integer
    #if 