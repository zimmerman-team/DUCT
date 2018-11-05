import numpy as np
import pandas as pd
import json
import datetime
import math
from indicator.models import DATAMODEL_HEADINGS, ADDITIONAL_HEADINGS, FILTER_HEADINGS, Indicator, Filters, Datapoints, DateFormat, FilterHeadings, ValueFormat
from geodata.models import SAVED_TYPES, Geolocation
from lib.tools import check_column_data_type, correct_data, convert_df
from lib.common import get_file_data, get_dtype_data, save_mapping, get_geolocation_dictionary
from metadata.models import File
from validate.validator import generate_error_data, save_validation_data
from api.indicator.views import reset_mapping
import pickle
import time

def begin_mapping(data):
    '''Perfoms manual mapping process.'''
    if 'dict' in data:
        final_file_headings = {}
        id = data['id']
        mappings = data['dict']

        ##Get relevant data
        save_mapping(id, mappings)
        empty_values_array, multi_entry_dict, data_model_dict, filter_headings_dict = split_mapping_data(mappings)
        df_data = get_file_data(id)
        error_data, dtypes_dict = get_dtype_data(id)
        ##Apply missing values
        df_data, mappings, dtypes_dict = apply_missing_values(df_data, data_model_dict, dtypes_dict, empty_values_array)

        result, correction_mappings, context = check_mapping_dtypes(data_model_dict, dtypes_dict)
        if not result:
            print(context)
            return context  # Bad mapping

        # TODO multiple categories/date situation
        if len(data_model_dict['date']) > 1 or len(data_model_dict['value']) > 1:
            ###Convert csv
            # if multi_entry_dict['relationship']:#check if unit of measure exists
            #    df_data, dtypes_dict, mappings = convert_df(df_data, multi_entry_dict, data_model_dict, filter_headings_dict, empty_values_array[4], dtypes_dict)
            print('TODO')
            #convert file into standard format

        ###TODO Group categories here
        if len(mappings['filters']) > 1:
            # if len(mappings['filter']) > 1:
            #   df_data, mappings, dtypes_dict, tmp_mapping = group_filters(df_data, dtypes_dict, multi_entry_dict, data_model_dict, filter_headings_dict)
            print('TODO')
        else:###TODO normal situation
            filter_file_column = data_model_dict['filters'][0]
            df_data['headings'] = filter_headings_dict['headings'][filter_file_column]
            data_model_dict['headings'] = ['headings']

        ##Need to change this
        error_lines, new_dtypes_dict = generate_error_data(df_data)
        save_validation_data(error_lines, id, new_dtypes_dict)

        for key in new_dtypes_dict:
            dtypes_dict[key] = new_dtypes_dict[key]

        reverse_mapping = {}
        for key in data_model_dict:
            if data_model_dict[key]:
                final_file_headings[key] = data_model_dict[key][0]
                reverse_mapping[data_model_dict[key][0]] = key

        print('Normalise data')
        df_data = correct_data(df_data, correction_mappings, error_lines, final_file_headings)

        #The sections of data model that are not allowed to be empty
        filter_applied = (df_data[final_file_headings['indicator']].notnull() & df_data[final_file_headings['date']].notnull()
                        & df_data[final_file_headings['value']].notnull() & df_data[final_file_headings['geolocation']].notnull())

        ##Remove empty values
        df_data = df_data[filter_applied].reset_index()
        #Convert all dates to numbers

        df_data[final_file_headings['date']] = pd.to_numeric(df_data[final_file_headings['date']]).astype(int)
        

        instance, created = DateFormat.objects.get_or_create(type = 'YYYY')#temp
        if created:
            instance.save()

        final_file_headings['date_format'] = 'date_format'
        reverse_mapping['date_format'] = 'date_format'
        final_file_headings['metadata'] = 'metadata'
        reverse_mapping['metadata'] = 'metadata'

        metadata = File.objects.get(id=id)
        df_data['metadata'] = metadata
        df_data['date_format'] = instance

        ind_dict, headings_dict, geolocation_dict, value_format_dict, filters_dict = get_save_unique_datapoints(df_data, final_file_headings, metadata.source, instance)
        dicts = [ind_dict, headings_dict, geolocation_dict, value_format_dict, filters_dict]

        print('save datapoints')
        save_datapoints(df_data, final_file_headings, reverse_mapping, dicts)

        context = {'success' : 1}
        return context
    else :
        context = {'error_messages' : 'No data in dictionary sent', 'success' : 0}
        return context


def split_mapping_data(mappings):
    empty_values_array = [mappings.pop('empty_indicator', None), 
                          mappings.pop('empty_geolocation', None),
                          mappings.pop('empty_geolocation_type', None),
                          mappings.pop('empty_filter', None),
                          mappings.pop('empty_value_format', None), 
                          mappings.pop('empty_date', None)]
    multi_entry_dict = {'relationship': mappings.pop('relationship', None), 'left_over': mappings.pop('left_over', None)}
    data_model_dict = { heading: mappings[heading] for heading in DATAMODEL_HEADINGS}
    filter_headings_model_dict = {heading: mappings[heading] for heading in FILTER_HEADINGS}
    return empty_values_array, multi_entry_dict, data_model_dict, filter_headings_model_dict


def group_filters(df_data, dtypes_dict, multi_entry_dict, data_model_dict):
    '''Begins process for grouping =filters together.
    
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
    '''

    #ignore relationship

    df_data['filter'] = ''
    df_data['heading_filter'] = ''
    tmp_mappings = ['filter']
    count = 0

    for value in data_model_dict['filter']:
        #loop through data combine with heading name and itself   
        if not multi_entry_dict['relationship']:#no relationshup defined
                df_data['filter'] = df_data['filter'] + '|' + df_data[value].map(str)
                df_data['heading_filter'] = df_data['heading_filter'] + '|' + value
        else:
            if not (value in relationship_dict):
                df_data['indicator_filter'] = df_data['indicator_filter'] + '|' + df_data[value].map(str)
                df_data['heading_filter'] = df_data['heading_filter'] + '|' + value
            else:
                tmp_mappings.append(value)
    mappings[key] = tmp_mappings#IF RELATIONSHOip add here????
    dtypes_dict[mappings['indicator_filter'][0]] = [('str','str')]

    return df_data, mappings, dtypes_dict, tmp_mappings


def apply_missing_values(df_data, mappings, dtypes_dict, empty_values_array):
    '''Appliess missing values to dataframe.
    
    Args:
        df_data (Dataframe): dataframe of CSV file.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        empty_values_array ([str]): values related to missing values in manual mapping process

    Returns: 
        df_data (Dataframe): dataframe of CSV file.
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
    '''
    indicator_value, geolocation_value, geolocation_type_value, filter_value, value_format_value, date_value = empty_values_array
    print('empty_value_array ', empty_values_array)

    if indicator_value:
        mappings['indicator'] = ['indicator']
        df_data['indicator'] = indicator_value
        dtypes_dict[mappings['indicator'][0]] = [('text', 'text')]
        #add indicator value as column 

    if geolocation_value:
        mappings['geolocation'] = ['geolocation']
        df_data['geolocation'] = geolocation_value
        dtypes_dict[mappings['geolocation'][0]] = [(geolocation_type_value, geolocation_type_value)]

    if filter_value:
        mappings['filter'] = ['filter']
        df_data['filter'] = filter_value
        dtypes_dict[mappings['filter'][0]] = [('text', 'text')]

    if date_value:
        mappings['date'] = ['date']
        df_data['date'] = date_value
        dtypes_dict[mappings['date'][0]] = [('date', 'date')]

    if value_format_value:##Only for one category
        if len(value_format_value.keys()) < 2 :#chect each entry emoty unit_of measure a dict
            mappings['value_format'] = ['value_format']
            print(value_format_value.keys())
            df_data['value_format'] = value_format_value[list(value_format_value.keys())[0]]
            dtypes_dict[mappings['value_format'][0]] = [('text', 'text')]

    return df_data, mappings, dtypes_dict


def check_mapping_dtypes(mappings, dtypes_dict):
    '''Begins process of checking if mapped columns are suitable.
    
    Args:
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.

    Returns: 
        result: indicates whether there is a bad mapping or not.
        correction_mappings ({str:(str,str)}): the conversion needed for each file heading.
        context ({str:[data]}): the information displayed to the user if mapping is bad.
    '''
    print('Checking data types')
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

    context = {'error_messages' : error_message, 'success' : 0}
    return (not len(error_message) > 0), correction_mappings, context 


def get_save_unique_datapoints(df_data, final_file_headings, file_source, date_format):
    '''Gets foreign keys for IndicatorDatapoint and saves new entries if needed.

    Args:
        df_data (Dataframe): dataframe of CSV file.
        final_file_headings ({str:[str]}): data model section and associated column heading.

    Returns:
        ind_dict ({str:Indicator}): dictionary of Indicator objects.
        ind_source_dict ({str:IndicatorSource}): dictionary of IndicatorSource objects.
        ind_country_dict ({str:Country}): dictionary of Country objects.
    '''

    count  = 0
    ind_dict = {}
    filters_dict = {}
    headings_dict = {}
    geolocation_dict = {}
    value_format_dict = {}

    unique_indicator = df_data[final_file_headings['indicator']].unique() #Important returns a list
    unique_geolocation = df_data[final_file_headings['geolocation']].unique()
    unique_headings = df_data.groupby([final_file_headings['indicator'], final_file_headings['headings']]).size().reset_index() #Important returns a dataframe
    unique_value_format = df_data[final_file_headings['value_format']].unique()
    unique_filters = df_data.groupby([final_file_headings['indicator'], final_file_headings['headings'], final_file_headings['filters']]).size().reset_index() #Important returns a dataframe
    unique_filter_value_formats = df_data.groupby([final_file_headings['indicator'],
                                      final_file_headings['headings'],
                                      final_file_headings['filters'],
                                      final_file_headings['value_format'],
                                      ]).size().reset_index()
    unique_filter_date_formats = df_data.groupby([final_file_headings['indicator'],
                                            final_file_headings['headings'],
                                            final_file_headings['filters'],
                                            final_file_headings['date_format'],
                                            ]).size().reset_index()
    unique_filter_geolocation_formats = df_data.groupby([final_file_headings['indicator'],
                                           final_file_headings['headings'],
                                           final_file_headings['filters'],
                                           final_file_headings['geolocation'],
                                           ]).size().reset_index()

    unique_lists = [unique_indicator, unique_headings, unique_geolocation, unique_value_format, unique_filters]
    count = 0

    ##unique list is not always the same datatype, consists of lists and dataframes
    for unique_list in unique_lists:
        for i in range(len(unique_list)):
            if(count == 0):#indicator
                instance, created = Indicator.objects.get_or_create(name=unique_list[i], file_source=file_source)
                if created:
                    instance.save()
                ind_dict[unique_list[i]] = instance
            elif(count == 1):#heading
                instance, created = FilterHeadings.objects.get_or_create(
                    name=unique_list[final_file_headings['headings']][i],##df_groupby[heading used in file][row of entry] #Quite confusing!!
                    indicator=ind_dict[unique_list[final_file_headings['indicator']][i]])#.first()
                if created:
                    instance.save()
                headings_dict[unique_list[final_file_headings['indicator']][i] + unique_list[final_file_headings['headings']][i]] = instance
            elif(count == 2):#Location#
                instance = Geolocation.objects.get(tag=unique_list[i])
                geolocation_dict[unique_list[i]] = instance  # shold use get?
            elif(count == 3):
                instance, created = ValueFormat.objects.get_or_create(type=unique_list[i])
                if created:
                    instance.save()
                value_format_dict[unique_list[i]] = instance
            else:#Filters
                ##Loop if mutiple fields
                instance, created = Filters.objects.get_or_create(
                    name=unique_list[final_file_headings['filters']][i],
                    heading=headings_dict[unique_list[final_file_headings['indicator']][i] + unique_list[final_file_headings['headings']][i]])
                if created:
                    instance.save()

                filters_dict[unique_list[final_file_headings['indicator']][i] + unique_list[final_file_headings['headings']][i]
                                          + unique_list[final_file_headings['filters']][i]] = instance
                ##Loop here
                instance.value_format =  value_format_dict[unique_filter_value_formats[final_file_headings['value_format']][i]]
                instance.date_format = date_format#[df_data[final_file_headings['date_format']][i]] + instance.date_formats
                instance.metadata = df_data['metadata'][0]
                geo_filter = unique_filter_geolocation_formats[final_file_headings['filters']] == unique_list[final_file_headings['filters']][i]
                for index, row in unique_filter_geolocation_formats[geo_filter].iterrows(): #TODO Vectorise
                    instance.geolocations.add(geolocation_dict[row[final_file_headings['geolocation']]])
                instance.save()

        count += 1
    return ind_dict, headings_dict, geolocation_dict, value_format_dict, filters_dict

def save_datapoints(df_data, final_file_headings, reverse_mapping, dicts):
    '''Saves each line that is valid of csv file to data model.
    
    Args:
        df_data (Dataframe): data of csv file in a dataframe.
        final_file_headings ({str: str}): contains data points as headings and columns as values.
        reverse_mapping ({str: str}): inverse of final_file_headings.
        dicts ([str:{str:Model}]): list of dictionaries containing foreign keys.
    '''

    metadata = df_data['metadata'][0]

    ind_dict, headings_dict, geolocation_dict, value_format_dict, filters_dict = dicts
    f1 = (lambda x: Datapoints(**x) )
    f2 = (lambda x, y: x.datapoints.add(y))##remove save()will be slow
    f3 = (lambda x: x.save())##remove save()will be slow

    vfunc = np.vectorize(f1)
    vfunc2 = np.vectorize(f2)
    vfunc3 = np.vectorize(f3)

    ###########TODO LOOP here for filters###################
    df_data[final_file_headings['filters']] = df_data[final_file_headings['indicator']] + df_data[
        final_file_headings['headings']] + df_data[final_file_headings['filters']]
    df_data[final_file_headings['filters']] = df_data[final_file_headings['filters']].map(filters_dict)

    ##TMP #Loop here
    df_filters = df_data[final_file_headings['filters']]
    df_data.drop([final_file_headings['filters']], axis=1, inplace=True)
    ######################################
    df_data[final_file_headings['indicator']] = df_data[final_file_headings['indicator']].map(ind_dict)
    df_data[final_file_headings['value_format']] = df_data[final_file_headings['value_format']].map(value_format_dict)
    df_data[final_file_headings['geolocation']] = df_data[final_file_headings['geolocation']].map(geolocation_dict)

    #df_data[final_file_headings['headings']] = df_data[final_file_headings['indicator']] + df_data[final_file_headings['headings']]
    #df_data[final_file_headings['headings']].map(headings_dict)

    #Not part of Datapoints table
    df_data.drop(['headings'], axis=1, inplace=True)
    reverse_mapping.pop('headings')

    reverse_mapping.pop(final_file_headings['filters'])##We don't use headings in data model

    column_list = list(reverse_mapping.keys())

    df_data = df_data[column_list]#should do this earlier
    df_data = df_data.rename(index=str, columns=reverse_mapping)#rename columns to data model

    batch_size = int(math.ceil(df_data['indicator'].size/100000))
    print(batch_size, ' batches')
    previous_batch = 0
    next_batch = 0

    for i in range(batch_size):
        next_batch += 100000 
        if next_batch > df_data['indicator'].size: #shouldn't be needed
            next_batch = df_data['indicator'].size
            i = batch_size + 1 #shouldn't happen
            print('Last batch, i set to ', i)

        print('Bulk saving')
        data_to_save = df_data[previous_batch:next_batch].to_dict(orient='records')#Get batch

        if(len(data_to_save) > 0):
            bulk_list = vfunc(np.array(data_to_save))#Vectorised operation, convert batch into datapoint objects
            data = Datapoints.objects.bulk_create(list(bulk_list))#Bulk create datapoints
            bulk_list = [] #Bulk list emptied to free space

            #######TODO: Loop here through filters######
            filter_data = np.array(df_filters[previous_batch:next_batch])#Get filter batch
            vfunc2(filter_data, np.array(data))#vectorised operation to add many to many mapping between filters and datapoints
            vfunc3(filter_data)#vectorised operation to save new addition methods, maybe best to do this last
            #########################################
            df_data[previous_batch:next_batch] = np.nan #Done to free space

            print('Previous batch ', previous_batch)
            print('Next batch ', next_batch)
            previous_batch = next_batch
        else:
            print('Nothing to save, error is occuring!!')#shouldn't happen
            print('I ', i)
            print('Previous batch ', previous_batch)
            print('Next batch ', next_batch)
            i =  df_data['indicator'].size + 1

    metadata.file_status = 4
    metadata.save()

'''Saves a dataframe temporarily'''
def temp_save_file(df_data):
    path = os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/tmpfiles')
    dtype_name = path +  '/' + str(uuid.uuid4()) + '.txt'
    with open(dtype_name, 'w') as f:
        pickle.dump(df_data, f)
    return dtype_name

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
            context = {'data' : {'id' : str(file.id), 'dict' : json.loads(file.mapping_used)}}
            begin_mapping(context)

