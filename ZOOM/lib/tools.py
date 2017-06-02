import strict_rfc3339
from functools import wraps  # use this to preserve function signatures and docstrings
from geodata.models import Country
from indicator.models import IndicatorDatapoint
from geodata.models import get_dictionaries
from collections import Counter
from dateutil.parser import parse
import pandas as pd
import numpy as np
import unicodedata
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
def identify_col_dtype(column_values, file_heading, dicts, sample=None): #only takle a sample of three value and serach for data type
    #   if sample != "None":
    #    #provide sample data with indexes
    #    #df_file[heading].sample(n=sample_amount)

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

    #iso2_codes_dict = dicts[0]
    #iso3_codes_dict = dicts[1]
    #country_names_dict = dicts[2]

    
    for value in column_values:
        #if string
        print(value)
        #print(str(value).lower())
        result = False
        try:
            try:
                temp_value = str(value.lower())
            except Exception:#special_character
                temp_value = str(unicodedata.normalize('NFKD', value).lower().encode('ascii','ignore'))
            result = (temp_value in dicts)
            if result: 
                error_counter.append((dicts[temp_value],counter))
                dtypes_found.append(dicts[temp_value])
        except Exception:
            print("Unicode error, checking if another datatype")

            """if value in iso2_codes_dict:#try:#change to if statements, expections more costly than ifs
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
            #check for country codes"""

            #if not check_dtype:
        if not result: 
            if "time" in file_heading.lower() or "date" in file_heading.lower() or "year" in file_heading.lower():# assuming time or date will have appropiate heading
                try: 
                    check_dtype = parse(str(value))
                    check_dtype = check_dtype.year
                    error_counter.append(("date", counter))
                    dtypes_found.append("date")
                except ValueError:
                    dtypes_found.append("date")#fix this
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
    if field == "country":
        #print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        country_list = ['iso2', 'iso3', "country_name"]
        #print(dtypes)
        #print(country_list)
        dtype_set = set(dtypes) & set(country_list)
        result = bool(dtype_set)   
        #print(result)

        if not result:
            dtype_set = dtypes[0]
            #print(dtype_set)
        else:
            indexes = []
            dtype_set = list(dtype_set)
            #print(dtype_set)
            for i in range(len(dtype_set)):#looking for furthest forward data type found that is  compatiable
                #print(dtypes.index(dtype_set[i]))
                indexes.append(int(dtypes.index(dtype_set[i])))
            #print(indexes)
            indexes.sort()
            
            #print("Indexes ", indexes)
            #print(indexes[0])
            dtype_set = dtypes[indexes[0]]#pointless??
            #print(dtype_set)

        # if "country_name" == dtype_set:
        #     dtype_set = "countrname"
        # elif "iso2" == dtype_set:
        #     dtype_set = "code"
            
        return result, dtype_set, "iso2" #return type found
    
    elif field == "measure_value":
        if "numeric" in dtypes:
            return True, "numeric" , "numeric"#("numeric" in dtypes), ["numeric"]
        else:
            return False, dtypes[0], "numeric"
    
    elif field == "date_value":
        if "date" in dtypes:#just return this
            return True, "date" , "date"
        else:
            return False, dtypes[0] , "date"
    else:#string
        return True, "str", "str" 


def correct_data(df_data, correction_data):#correction_data ["country_name, iso2, iso3 etc"]
    
    value = {}
    _, dicts = get_dictionaries()
    #print("Lets go")
    for key in correction_data:
        #decide what format to goive it too #also check date
        #print("og loc")
        #print(df_data.head())
        #print("----------------------------------")
        #print(correction_data[key])
        if correction_data[key][1] == "iso2":
            #model = Country.objects.all()
            try:
                df_data[key] = df_data[key].str.lower().astype("str")
            except Exception:#special_character
                f = (lambda x: str(unicodedata.normalize('NFKD', x).lower().encode('ascii','ignore')))
                df_data[key] = df_data[key].apply(f).astype("str")
            #df_data[key] = df_data[key].str.lower()
            if correction_data[key][0] == "country_name":
                #print("Name")
                curr_dicts = dicts["country_name"]
                #print(curr_dicts, " key ", key)
                df_data[key].replace(curr_dicts, inplace=True) #needs to be more comprehensive, users mix iso2 and iso3 in column data
                #print(df_data[key].head())
            elif correction_data[key][0] =="iso3":#not needed??
                #print("iso3")
                curr_dicts = dicts["iso3"]
                df_data.replace(curr_dicts, inplace=True)
            #print("end")
            #print("key ", key)
            #print(df_data.head())
            #print(fgs)
        elif correction_data[key][1] == "date":
            #print(df_data[key])
            #f = (lambda x: parse(str(x)).year)
            try:
                old = df_data[key]
                df_data[key] = pd.to_datetime(df_data[key])
                df_data[key] = df_data[key].year.astype(int)
                #df_data[key] = df_data[key].apply(f)
            except Exception:
                df_data[key] = old
                f = (lambda x: parse(str(int(x))).year)#2016.0 will cause error unless it is formatted
                try:
                    df_data[key] = df_data[key].apply(f)
                except Exception:
                    df_data[key].apply(lambda x: lookForError(f, "0000", x)) 
        elif correction_data[key][1] == "str":
            #print("string")
            f = (lambda x: str(x).decode("unicode_escape").encode('ascii','ignore'))
            df_data[key] = df_data[key].apply(f)

        #elif date
        #elif measure value etc
            
            """for i in range(len(df_data[key])):
                value[correction_data[key][0]] = df_data[key][i] #might not work?
                #query_result = model.filter(**value)
                
                if  df_data[key][i] in curr_dicts:
                    model_value = curr_dicts[df_data[key][i]][0]#query_result[0].code
                else:
                    model_value = "NA"
                df_data[key][i] = model_value"""
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


def lookForError(f, default, x):
    try:
        value = f(x)
    except Exception:
        value = default
    return default

def convert_df(mappings,relationship_dict, left_over_dict, df_data, dtypes_dict, empty_unit_measure_value):
    
    if not empty_unit_measure_value:
        empty_unit_measure_value = {}

    columns = []
    for col in df_data.columns: 
        temp = str(col)#.replace(" ", "~")#needed?
        col = str(col) 
        if (temp in relationship_dict):
            if not relationship_dict[temp] in columns or not left_over_dict[temp] in columns:
                columns.append(str(relationship_dict[temp]))
                columns.append(str(left_over_dict[temp]))
        else: 
            columns.append(col)

    columns = list(set(columns))#filter duplicates
    columns_set = list(set(list(columns)) & set(list(df_data.columns))) #set(columns).intersection(set(df_data.columns)) 
    new_df = pd.DataFrame( columns = columns)
    
    counter = 0
    new_df['unit_of_measure'] = 0

    for i in range(len(df_data[columns_set[0]])):#columns[0] bad idea, fix
        #for col in columns_set:
        #    new_df[col][counter] = df_data[col][i]
        for col in relationship_dict:

            if relationship_dict[col] == "date_value":
                dtypes_dict[relationship_dict[col]] = [['date', "100%"]] # check type #######################check here data type
            else:
                dtypes_dict[relationship_dict[col]] = [['str', "100%"]] # check type #######################check here data type

            dtypes_dict[left_over_dict[col]] = [['numeric', '100%']]
            ##loop here through the values for relationship   
            #don't need column
            
            new_df.loc[counter] = df_data.iloc[i] #copy row
            #might have to be greater than 2
            
            if col in mappings['indicator_category'] and len(mappings['indicator_category']) > 1:#if more than one relationship ie multiple subgroupd and relationships
                check  = new_df[relationship_dict[col]][counter] #if supgroup already defined
                new_df[relationship_dict[col]][counter] = new_df[relationship_dict[col]][counter] + "|" + (col.replace("~", " "))#last part not needed
                new_df[left_over_dict[col]][counter] = df_data[col.replace("~", " ")][i]#check if col_replace is there
                #if empty_unit_of_measure in mappings:
                #apply units of measure
                #a = 5                        
                
            else: #normal case
                #hre.y 
                new_df[relationship_dict[col]][counter] = col.replace("~", " ")#add column heading
                new_df[left_over_dict[col]][counter] = df_data[col.replace("~", " ")][i]
            
            if col.replace("~", " ") in empty_unit_measure_value:
                #print("getting unit of measure")
                #print(col.replace("~", " "))
                #print(empty_unit_measure_value[col.replace("~", " ")])
                new_df['unit_of_measure'][counter] = empty_unit_measure_value[col.replace("~", " ")]
            #new_df  = df_data[mappings[key]]
            #map value
            
            #mappings[relationship_dict[col]] = [relationship_dict[col]]#what is the point of this?
            #mappings[left_over_dict[col]] = [left_over_dict[col]] 

            counter += 1
        #if i == 2:
        #    sdf.sgd
    return new_df#.T.drop_duplicates().T#prevent duplicate columns// why is this happening

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

