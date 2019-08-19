import datetime
import json
import math
import os
import pickle
import uuid

import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models import Max, Min

from api.indicator.views import reset_mapping
from geodata.models import Geolocation, PointBased
from indicator.models import (FILTER_HEADINGS, Datapoints, DateFormat,
                              FilterHeadings, Filters, Indicator, ValueFormat)
from lib.common import get_dtype_data, get_file_data
from lib.tools import check_column_data_type, convert_df, correct_data
from metadata.models import File
from validate.validator import generate_error_data, save_validation_data


def begin_mapping(data):
    # Performs manual mapping process
    if 'mapping_dict' in data:
        final_file_headings = {}
        id = data['metadata_id']

        # Get relevant data
        # save_mapping(id, instance)

        df_data = get_file_data(id)

        data_model_dict, filter_headings_dict, empty_entries_dict, \
            multi_entry_dict, point_base_dict = split_mapping_data(data)
        error_data, dtypes_dict = get_dtype_data(id)

        # Check if any new Geolocation information to save
        if 'coord' in point_base_dict and \
                not point_base_dict['coord']['lat'] == '':
            # shoud save here and get later
            lat = point_base_dict['coord']['lat']
            lon = point_base_dict['coord']['lon']
            df_data['geolocation'] = 'pointbased'
            dtypes_dict['geolocation'] = df_data['geolocation'].copy()
            df_data['geolocation'] = df_data[lon].astype(
                str) + "," + df_data[lat].astype('str')
            data_model_dict['geolocation'] = ['geolocation']
            # drop the two columns
            dtypes_dict.pop(lat, None)
            dtypes_dict.pop(lon, None)
            df_data.drop([lon, lat], inplace=True, axis=1)

            # dtypes_dict['geolocation'] =
            point_based = True
        else:
            point_based = False

        # Reformat dataframe for dates or categories
        if len(data_model_dict['value']) > 1:
            df_data, dtypes_dict, data_model_dict = convert_df(
                df_data, multi_entry_dict, data_model_dict,
                empty_entries_dict.pop('empty_value_format'), dtypes_dict)

        # Apply missing values
        df_data, data_model_dict, dtypes_dict = apply_missing_values(
            df_data, data_model_dict, dtypes_dict, empty_entries_dict)

        # Check if datatypes of data is correct
        result, correction_mappings, context = check_mapping_dtypes(
            data_model_dict, dtypes_dict)

        if not result:
            print(context)
            # return context  # Bad mapping
            raise Exception(context)

        # TODO: check is new_dtypes_dict necessary
        # why can't this be moved in front of check mappings?
        # Could be important if user wants to see which parts of data did not
        # get mapped and why they did not
        error_lines, new_dtypes_dict = generate_error_data(df_data)
        save_validation_data(error_lines, id, dtypes_dict)

        # TODO: check is this is needed
        for key in new_dtypes_dict:
            dtypes_dict[key] = new_dtypes_dict[key]

        # Get the reverse mapping of data_model_dict
        # TODO: check if this is needed
        final_file_headings = {}
        for key in data_model_dict:
            if data_model_dict[key]:
                if key == 'filters':
                    final_file_headings[key] = data_model_dict[key]
                else:
                    final_file_headings[key] = data_model_dict[key][0]

        # Normalise data
        df_data = correct_data(df_data, correction_mappings, error_lines,
                               final_file_headings, point_based)

        # Filter out bad data from datafram
        filter_applied = (
            df_data[final_file_headings['indicator']].notnull()
            # The sections of data model
            # are not allowed to be empty
            & df_data[final_file_headings['date']].notnull()
            & df_data[final_file_headings['value']].notnull()
            & df_data[final_file_headings['geolocation']].notnull())

        df_data = df_data[filter_applied].reset_index()  # Remove empty values
        df_data[final_file_headings['date']] = pd.to_numeric(
            # Convert all dates to numbers
            # TODO: check is this needed, normalise should do this
            df_data[final_file_headings['date']]).astype(int)

        # Create missing entries that are used in Datapoints datamodel
        instance, created = DateFormat.objects.get_or_create(
            type='YYYY')  # Todo make dynamic
        if created:
            instance.save()

        final_file_headings['date_format'] = 'date_format'
        final_file_headings['metadata'] = 'metadata'

        metadata = File.objects.get(id=id)
        df_data['metadata'] = metadata
        df_data['date_format'] = instance

        # Save and get foreign key data for datapoints model
        ind_dict, headings_dict, geolocation_dict, value_format_dict, \
            filters_dict = get_save_unique_datapoints(
                df_data, final_file_headings, metadata, instance,
                filter_headings_dict, point_based)

        # Save Datapoints
        dicts = [
            ind_dict, headings_dict, geolocation_dict, value_format_dict,
            filters_dict
        ]

        save_datapoints(df_data, final_file_headings, filter_headings_dict,
                        dicts)

        context = {'success': 1}
        return context
    else:
        context = {
            'error_messages': 'No data in dictionary sent',
            'success': 0
        }
        raise context


def split_mapping_data(data):
    data_model_dict = data['mapping_dict']
    filter_headings_dict = data[FILTER_HEADINGS]
    if 'extra_information' in data:
        empty_entries_dict = data['extra_information']['empty_entries'] \
            if 'empty_entries' in data['extra_information'] else {
        }
        multi_entry_dict = data['extra_information']['multi_mapped'] \
            if 'multi_mapped' in data['extra_information'] else {
        }
        point_base_dict = data['extra_information']['point_based_info'] \
            if 'point_based_info' in data['extra_information'] else {}
    else:
        empty_entries_dict = {}
        multi_entry_dict = {}
        point_base_dict = {}
    return data_model_dict, filter_headings_dict, empty_entries_dict, \
        multi_entry_dict, point_base_dict


def apply_missing_values(df_data, mappings, dtypes_dict, empty_entries_dict):
    """
    Applies missing values to dataframe.
    """

    length = (len(df_data[df_data.columns[0]]) - 1)

    if 'empty_indicator' in empty_entries_dict and not empty_entries_dict[
            'empty_indicator'] == '':
        mappings['indicator'] = ['indicator']
        df_data['indicator'] = empty_entries_dict['empty_indicator']
        dtypes_dict[mappings['indicator'][0]] = ['text'] * length
        # add indicator value as column

    if 'empty_geolocation' in empty_entries_dict and not empty_entries_dict[
            'empty_geolocation']['value'] == '':
        mappings['geolocation'] = ['geolocation']
        df_data['geolocation'] = \
            empty_entries_dict['empty_geolocation']['value']
        dtypes_dict[mappings['geolocation'][0]] = [
            empty_entries_dict['empty_geolocation']['type']
        ] * length

    if 'empty_filter' in empty_entries_dict and \
            not empty_entries_dict['empty_filter'] == '':
        mappings['filters'] = ['filters']
        df_data['filters'] = empty_entries_dict['empty_filter']
        dtypes_dict[mappings['filters'][0]] = ['text'] * length

    if 'empty_date' in empty_entries_dict and\
            not empty_entries_dict['empty_date'] == '':
        mappings['date'] = ['date']
        df_data['date'] = empty_entries_dict['empty_date']
        dtypes_dict[mappings['date'][0]] = ['date'] * length

    if 'empty_value_format' in empty_entries_dict and len(
            empty_entries_dict['empty_value_format']) > 0:
        if len(mappings['value']) <= 1:
            # check each entry empty value format dict
            mappings['value_format'] = ['value_format']
            df_data['value_format'] = \
                empty_entries_dict['empty_value_format'][list(
                    empty_entries_dict['empty_value_format'].keys())[0]]
            dtypes_dict[mappings['value_format'][0]] = ['text'] * length
        else:
            print('Shouldn\' happen')
            # TODO: hande multiple value formats
            # TODO: reformat df data and apply multiple formats
            # mappings['value_format'] = ['value_format']
            # dtypes_dict[mappings['value_format'][0]] = [('text', 'text')]

    if 'empty_value' in empty_entries_dict and \
            not empty_entries_dict['empty_value'] == '':
        mappings['value'] = ['value']
        df_data['value'] = empty_entries_dict['empty_value']
        dtypes_dict[mappings['value'][0]] = ['numeric'] * length

    return df_data, mappings, dtypes_dict


def check_mapping_dtypes(mappings, dtypes_dict):
    '''Begins process of checking if mapped columns are suitable.

    Args:
        mappings ({str:[str]}): the users chosen mappings for a file column.
        dtypes_dict ({str:str}): stores the data-types found for each heading.

    Returns:
        result: indicates whether there is a bad mapping or not.
        correction_mappings ({str:(str,str)}): the conversion needed
        for each file heading.
        context ({str:[data]}): the information displayed to the user
        if mapping is bad.
    '''
    correction_mappings = {}
    error_message = []
    for key in mappings:
        if mappings[key]:  # this is included incase no mapping is given
            for heading in mappings[key]:
                correction_mappings[heading] = []
                temp_results_check_dtype, temp_found_dtype, \
                    temp_convert_dtype = \
                    check_column_data_type(key, dtypes_dict[heading])

                if temp_results_check_dtype:
                    correction_mappings[heading] = (temp_found_dtype,
                                                    temp_convert_dtype)
                else:
                    error = [
                        heading, key, temp_found_dtype, temp_convert_dtype
                    ]
                    error_message.append(error)  # datatype blah blah

    context = {'error_messages': error_message, 'success': 0}
    return (not len(error_message) > 0), correction_mappings, context


def get_save_unique_datapoints(df_data,
                               final_file_headings,
                               file,
                               date_format,
                               filter_headings_dict,
                               point_based=False):
    """
    Gets foreign keys for IndicatorDatapoint and saves new entries if needed.
    """

    count = 0
    ind_dict = {}
    filters_dict = {}
    headings_dict = {}
    geolocation_dict = {}
    value_format_dict = {}

    # Important returns a list
    unique_indicator = df_data[final_file_headings['indicator']].unique()
    unique_geolocation = df_data[final_file_headings['geolocation']].unique()
    unique_value_format = df_data[final_file_headings['value_format']].unique()

    unique_lists = [
        unique_indicator,
        unique_geolocation,
        unique_value_format,
    ]

    print('Saving unique datapoints %s' % datetime.datetime.now())

    for unique_list in unique_lists:
        for i in range(len(unique_list)):
            if count == 0:  # indicator
                instance, created = Indicator.objects.get_or_create(
                    name=unique_list[i], file_source=file.source, file=file)
                if created:
                    instance.save()
                ind_dict[unique_list[i]] = instance
                for file_heading in filter_headings_dict:
                    heading_instance, created = \
                        FilterHeadings.objects.get_or_create(
                            # df_groupby[heading used in file][row of entry]
                            # Quite confusing!!
                            name=filter_headings_dict[file_heading],
                            indicator=instance)
                    if created:
                        heading_instance.save()
                    heading_index = unique_list[i] + \
                        filter_headings_dict[file_heading]
                    headings_dict[heading_index] = heading_instance

            elif count == 1:  # Location#
                if point_based:
                    lon = float(unique_list[i].split(',')[0])
                    lat = float(unique_list[i].split(',')[1])
                    point = Point(lon, lat)
                    p, created = PointBased.objects.get_or_create(
                        name=unique_list[i], center_longlat=point)
                    if created:
                        p.save()
                        instance = Geolocation(content_object=p,
                                               tag=unique_list[i],
                                               type='pointbased')
                        instance.save()
                    else:
                        instance = Geolocation.objects.get(tag=unique_list[i])
                else:
                    if isinstance(unique_list[i], str):
                        if len(unique_list[i]) == 2:
                            instance = Geolocation.objects.get(
                                iso2=unique_list[i])
                        elif len(unique_list[i]) == 3:
                            instance = Geolocation.objects.get(
                                iso3=unique_list[i])
                        else:
                            instance = Geolocation.objects.get(
                                tag=unique_list[i])
                    else:
                        instance = Geolocation.objects.get(tag=unique_list[i])

                geolocation_dict[unique_list[i]] = instance  # shold use get?
            else:
                instance, created = ValueFormat.objects.get_or_create(
                    type=unique_list[i])
                if created:
                    instance.save()
                value_format_dict[unique_list[i]] = instance
        count += 1

    # Save filters
    print('Saving filters')
    for j in range(len(final_file_headings['filters'])):
        unique_filters = df_data.groupby([
            final_file_headings['indicator'],
            # Important returns a dataframe
            final_file_headings['filters'][j]
        ]).size().reset_index()
        unique_filter_value_formats = df_data.groupby([
            final_file_headings['indicator'],
            final_file_headings['filters'][j],
            final_file_headings['value_format'],
        ]).size().reset_index()
        unique_filter_date_formats = df_data.groupby([
            final_file_headings['indicator'],
            final_file_headings['filters'][j],
            final_file_headings['date_format'],
        ]).size().reset_index()
        unique_filter_geolocation_formats = df_data.groupby([
            final_file_headings['indicator'],
            final_file_headings['filters'][j],
            final_file_headings['geolocation'],
        ]).size().reset_index()

        for i in range(len(unique_filters)):
            filter_name = unique_filters[final_file_headings['filters'][j]][i]
            indicator = unique_filters[final_file_headings['indicator']][i]
            filter_heading_name = \
                filter_headings_dict[final_file_headings['filters'][j]]
            instance, created = Filters.objects.get_or_create(
                name=filter_name,
                heading=headings_dict[indicator + filter_heading_name],
                indicator=ind_dict[indicator])
            if created:
                instance.save()

            filters_dict[indicator + filter_heading_name +
                         filter_name] = instance
            # Loop here
            instance.value_format = value_format_dict[
                unique_filter_value_formats[
                    final_file_headings['value_format']][i]]

            # [df_data[final_file_headings['date_format']][i]] +
            # instance.date_formats
            instance.date_format = date_format
            instance.metadata = df_data['metadata'][0]
            geo_filter = unique_filter_geolocation_formats[
                final_file_headings['filters'][j]] == unique_filters[
                    final_file_headings['filters'][j]][i]
            geolocation_list = list(
                unique_filter_geolocation_formats[geo_filter][
                    final_file_headings['geolocation']].map(
                        geolocation_dict))  # TODO Vectorise
            instance.geolocations.add(*geolocation_list)
            instance.save()

    # unique list is not always the same datatype, consists of lists and
    # dataframes
    print('Finsihed with unique datapoints %s' % datetime.datetime.now())

    return ind_dict, headings_dict, geolocation_dict, value_format_dict, \
        filters_dict


def save_datapoints(df_data, final_file_headings, filter_headings_dict, dicts):
    '''Saves each line that is valid of csv file to data model.

    Args:
        df_data (Dataframe): data of csv file in a dataframe.
        final_file_headings ({str: str}): contains data points as headings
        and columns as values.
        reverse_mapping ({str: str}): inverse of final_file_headings.
        dicts ([str:{str:Model}]): list of dictionaries
        containing foreign keys.
    '''

    metadata = df_data['metadata'][0]

    ind_dict, headings_dict, geolocation_dict, \
        value_format_dict, filters_dict = dicts
    f1 = (lambda x: Datapoints(**x))
    f2 = (lambda x, y: x.datapoints.add(*y))  # Really really slow
    f3 = (lambda x: x.save())  # remove save()will be slow

    vfunc = np.vectorize(f1)
    vfunc2 = np.vectorize(f2)
    vfunc3 = np.vectorize(f3)

    df_filters = pd.DataFrame(columns=final_file_headings['filters'])
    unique_df_filters = pd.DataFrame(columns=final_file_headings['filters'])

    for heading in final_file_headings['filters']:
        df_data['heading'] = filter_headings_dict[heading]
        df_data[heading] = df_data[final_file_headings['indicator']] \
            + df_data['heading'] + df_data[heading]
        df_filters[heading] = df_data[heading]
        unique_df_filters[heading] = np.unique(df_data[heading])
        df_filters[heading] = df_data[heading].map(filters_dict)
        unique_df_filters[heading] = unique_df_filters[heading].map(
            filters_dict)

    df_data.drop(final_file_headings['filters'], axis=1, inplace=True)
    filter_headings = final_file_headings.pop('filters', None)

    df_data[final_file_headings['indicator']] = df_data[
        final_file_headings['indicator']].map(ind_dict)
    df_data[final_file_headings['value_format']] \
        = df_data[final_file_headings['value_format']].map(value_format_dict)
    df_data[final_file_headings['geolocation']] \
        = df_data[final_file_headings['geolocation']].map(geolocation_dict)

    reverse_mapping = {}
    for heading in final_file_headings:
        reverse_mapping[final_file_headings[heading]] = heading

    column_list = list(reverse_mapping.keys())
    df_data = df_data[column_list]  # should do this earlier
    df_data = df_data.rename(index=str, columns=reverse_mapping)

    batch_size = int(math.ceil(df_data['indicator'].size / 100000))
    previous_batch = 0
    next_batch = 0

    count = 1
    for i in range(batch_size):
        print('Saving datapoints for batch %d %s' %
              (count, datetime.datetime.now()))
        next_batch += 100000
        if next_batch > df_data['indicator'].size:  # shouldn't be needed
            next_batch = df_data['indicator'].size
            i = batch_size + 1  # shouldn't happen

        data_to_save = df_data[previous_batch:next_batch].to_dict(
            orient='records')

        # if(len(data_to_save) > 0):
        # Vectorised operation, convert batch into datapoint objects
        bulk_list = vfunc(np.array(data_to_save))
        data = Datapoints.objects.bulk_create(
            list(bulk_list))  # Bulk create datapoints
        bulk_list = []  # Bulk list emptied to free space

        data = np.array(data)
        filter_data = df_filters[previous_batch:next_batch]  # Get filter batch
        print('Saving filters for batch %d %s' %
              (count, datetime.datetime.now()))
        for heading in filter_headings:
            print('Saving heading %s for batch %d %s' %
                  (heading, count, datetime.datetime.now()))
            # vectorised operation to add many to many mapping between filters
            # and datapoints
            for f in unique_df_filters[heading]:
                # print('f ', f)
                # print('Unique filters ', unique_filters[f])
                f.datapoints.add(*list(data[filter_data[heading] == f]))
                f.save()
            # vfunc2(np.array(filter_data[heading]), data)
            print('Added datapoints to filter %s' % (datetime.datetime.now()))
            # vectorised operation to save new addition methods, maybe best to
            # do this last
        # vfunc3(np.array(filter_data[heading]))
        print('Saved filters %s' % (datetime.datetime.now()))

        df_data[previous_batch:next_batch] = np.nan  # Done to free space

        print('Previous batch ', previous_batch)
        print('Next batch ', next_batch)
        previous_batch = next_batch
        print('Finished saving batch %d hurray! %s' %
              (count, datetime.datetime.now()))
        count += 1

    add_first_indicator_year(ind_dict)

    print('Finished')
    metadata.file_status = 4
    metadata.save()


def add_first_indicator_year(ind_dict):
    print('Saving indicators data first year')
    # so here we basically add the first
    # data point year to the indicators
    # that we've just created
    # so its not the best thing to do this
    # but thats how i made it #Morty :D
    # TODO redo this properly, maybe its possible
    # to save this first year while the csv
    # is getting read by pandas or sth
    for ind_key in ind_dict:
        ind_data = Datapoints.objects.filter(indicator=ind_dict[ind_key].id)
        #  so yeah currently this works with dates when they are only years
        #  or with simplo ISO standard date format
        biggest_date = ind_data.aggregate(Max('date'))
        #  i dunno why its stored like that... date__min...
        ind_dict[ind_key].last_data_year = biggest_date['date__max']
        ind_dict[ind_key].save()


def temp_save_file(df_data):
    path = os.path.join(os.path.dirname(settings.BASE_DIR),
                        'ZOOM/media/tmpfiles')
    dtype_name = path + '/' + str(uuid.uuid4()) + '.txt'
    with open(dtype_name, 'w') as f:
        pickle.dump(df_data, f)
    return dtype_name


def remap_all_files():
    files = File.objects.all()
    for file in files:
        if file.status == 5:
            context = {'data': {'file': str(file.id)}}
            reset_mapping(json.dumps(context,
                                     ensure_ascii=False))  # encoding error
            context = {
                'data': {
                    'id': str(file.id),
                    'dict': json.loads(file.mapping_used)
                }
            }
            begin_mapping(context)
