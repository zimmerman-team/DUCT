import re
import sys
import unicodedata
from collections import Counter

import dateutil.parser as date_parser
import numpy as np
import pandas as pd

from geodata.models import GEOTYPE_HEADINGS, Country, Geolocation
from indicator.models import Datapoints
from lib.common import get_geolocation_dictionary


def identify_col_dtype(column_values, file_heading, dicts):
    '''Identify the data types for each value in a column.

    Args:
        column_values (Series): values related to a column.
        file_heading (str): heading of the column.
        dicts ([{str:str}]): dictionaries for identifing geolocation data type.

    Returns:
        prob_list ([(str,str)]): a list of tuples containing the data type
        found and the percentage of data found of that type.
        error_counter ([str]): list of data types found
        for each cell in the column.
    '''

    # reload(sys)
    # sys.setdefaultencoding('utf-8') #not eccomended to use

    dtypes_found = []
    error_counter = column_values.astype('str')
    error_counter[:] = np.NaN
    not_null_filter = column_values.notnull()
    numeric_filter = pd.to_numeric(
        column_values[not_null_filter],
        errors='coerce').notnull()

    # Checking Date###
    error_counter = check_if_date(
        file_heading,
        column_values,
        not_null_filter,
        numeric_filter,
        error_counter)

    # Country Check###
    if(np.sum(error_counter.notnull()) < len(error_counter)):

        # Remove special characters
        # try:
        # unicode changed in python 3, below solution doesn't
        # work when comparing against strings anymore
        # f = (lambda x: str(unicodedata.normalize('NFKD', x).lower().
        # encode('ascii','ignore')).strip().replace('_', ' '))
        f = (lambda x: str(x.lower().replace('_', ' ')))
        filter_used = not_null_filter & (~numeric_filter)
        tmp_country_values = column_values[filter_used].apply(f)
        tmp_country_values = tmp_country_values.map(dicts)
        # get values that are not null => country
        country_filter = tmp_country_values.notnull()
        error_counter[filter_used] = tmp_country_values[country_filter]

    # Check if coordinates
    filter_used = (
        error_counter.isnull()) & (
        not_null_filter & (
            ~numeric_filter))

    ###Clean up###
    error_counter[~not_null_filter] = 'blank'

    filter_used = (
        error_counter.isnull()) & (
        not_null_filter & (
            ~numeric_filter))
    error_counter[filter_used] = 'text'

    filter_used = (error_counter.isnull()) & (not_null_filter & numeric_filter)
    error_counter[filter_used] = 'numeric'

    dtypes_found = np.unique(error_counter)
    prob_list = get_prob_list(error_counter)

    return prob_list, error_counter


def check_if_date(file_heading, column_values,
                  not_null_filter, numeric_filter, error_counter):
    '''Check if column values could be a date.

    Args:
        file_heading (str): heading of the file.
        column_values (Series): values related to a column.
        not_null_filter (np[boolean]): filters for non-null values.
        numeric_filter (np[boolean]): filters for numeric values.
        error_counter ([int]): error data, a list that will
        contain all data types for column_values.

    Returns:
        result (boolean): result of check.
        error_counter ([int]): error data, a list that will
        contain all data types for column_values.

    '''

    # assuming time or date will have appropiate heading, perhaps a bad
    # assumption
    result = 'time' in file_heading.lower() or 'date' in file_heading.lower(
    ) or 'year' in file_heading.lower() or 'period' in file_heading.lower()
    if result:
        filters = [not_null_filter & numeric_filter, not_null_filter & (
            ~numeric_filter)]  # [all numeric values, all string values]
        filter_types = ['int', 'string']
        for i in range(len(filters)):  # length of 2
            filter_applied = filters[i]
            values = column_values[filter_applied]
            if filter_types[i] == 'int':
                values = values.astype(int)
            # Find which values are suitable to be a date
            tmp_data_values = pd.to_datetime(
                values.astype('str'), errors='coerce')
            date_dtype_values = error_counter[filter_applied]

            # get values that are not null => date
            date_filter = tmp_data_values.notnull()
            date_dtype_values[date_filter] = 'date'
            # update error_counter
            error_counter[filter_applied] = date_dtype_values

    return error_counter


def get_prob_list(error_counter):
    '''Gets the probability listing of all data-types found'''
    prob_list = []
    normalisation = float(len(error_counter))
    for heading, count in Counter(error_counter).most_common():
        prob_list.append(
            (heading,
             '{0:.0f}%'.format(
                 float(count) /
                 normalisation *
                 100)))
    return prob_list


def update_cell_type(value, error_counter, line_no, file_heading):
    '''Used when checking just one cell so no vectorisation'''
    # sys.setdefaultencoding('utf-8')
    date_check_f = (lambda x: 'time' in x.lower() or 'date' in x.lower(
    ) or 'year' in x.lower() or 'period' in x.lower())
    date_f = (lambda x: date_parser.parse(str(x)))

    try:
        result = ''.join(str(value).split()) == ''
        if result:
            dtype = 'blank'
    except Exception:
        result = False

    if not value:
        dtype = 'blank'
    else:
        # Integer
        try:
            tmp = int(value)
            ##Checking Date###
            result = date_check_f(file_heading)
            if result:
                try:
                    tmp = date_f(tmp)
                    dtype = 'date'
                except Exception:
                    result = False

            if not result:
                dtype = 'numeric'
        # String
        except Exception:
            ####Checking Date###
            f = (lambda x: str(x).lower().strip().replace('_', ' '))
            #value = f(value)
            result = date_check_f(file_heading)

            if result:
                try:
                    value = date_f(value)
                    dtype = 'date'
                except Exception:
                    result = False

            ###Country Check###
            if(not result):
                value = f(value)
                result, dtype = check_if_cell_country(value)
            if(not result):
                dtype = 'text'

    error_counter[line_no] = dtype
    prob_list = get_prob_list(error_counter)
    return prob_list, error_counter


def check_if_cell_country(value):
    '''Checks if value is a country'''
    if len(str(value)) == 2:
        result = Geolocation.objects.filter(iso2=value).exists()
        return result, 'geotype'
    elif len(str(value)) == 3:
        result = Geolocation.objects.filter(iso3=value).exists()
        return result, 'geotype'
    else:
        result = Geolocation.objects.filter(tag=value).exists()
        return result, 'geotype'

    return False, ''


def check_column_data_type(field, dtypes):
    """Check that the data types found in a column is appropiate
    for the heading that it was matched to.

    Args:
        field (str): column heading.
        dtypes ([str]): list of dtypes found for a column heading.

    Returns:
        result (boolean), true or false if appropiate dtype found.
        dtype_set ([str]), matching data types found for mapping.
        conversion_dtype (str): the data type the column needs to
        be converted to.
    """

    dtypes = [i for i in dtypes]
    dtype_set = set()
    result = False
    if field == 'geolocation':
        geotype_list = GEOTYPE_HEADINGS
        dtype_set = set(dtypes) & set(geotype_list)
        result = bool(dtype_set)

        if not result:
            return False, dtypes[0], 'geotype'
        else:
            indexes = []
            dtype_set = list(dtype_set)

            for i in range(
                    len(dtype_set)):
                    # looking for furthest forward data
                    #  type found that is compatiable
                indexes.append(int(dtypes.index(dtype_set[i])))

            indexes.sort()
            dtype_set = dtypes[indexes[0]]  # pointless??
            return True, dtype_set, dtype_set

    elif field == 'value':
        if 'numeric' in dtypes:
            return True, 'numeric', 'numeric'
        elif'text' in dtypes:
            return True, 'text', 'numeric'
        else:
            return False, dtypes[0], 'numeric'

    elif field == 'date':
        if 'date' in dtypes:
            # Future: include format of date
            return True, 'date', 'date'
        else:
            return False, dtypes[0], 'date'
    else:
        return True, 'text', 'text'


# use validation error lines to get bad data, would optimise
# correction_data ['country_name, iso2, iso3 etc']
def correct_data(df_data, correction_data, error_data,
                 index_order, point_based=False):
    '''Corrects data for each column according to correction_data.

    Args:
        df_data (Dataframe): dataframe of CSV file.
        correction_mappings ({str:(str,str)}): the conversion
        needed for each file heading.
        error_data ({str:[str]}): error data for each column.
        index_order ({str: str}): contains data points as headings
         and columns as values.

    Returns:
        new_df (Dataframe): the converted dataframe.
    '''

    value = {}
    dicts = get_geolocation_dictionary()

    def clean_lambda(x): return x.strip().lower()

    for key in correction_data:
        not_null_filter = df_data[key].notnull()
        numeric_filter = pd.to_numeric(
            df_data[key][not_null_filter],
            errors='coerce').notnull()

        # Geolocation
        if correction_data[key][1] in GEOTYPE_HEADINGS:
            if not point_based:
                df_data[key] = df_data[key].str.lower()
                filter_used = not_null_filter & (~numeric_filter) & (
                    error_data[key][error_data[key] ==
                                    correction_data[key][0]])
                df_data[key] = df_data[key][filter_used]
        elif correction_data[key][1] == 'date':
            # Numeric check
            filter_applied1 = ((not_null_filter) & (numeric_filter) & (
                error_data[key][error_data[key] == correction_data[key][0]]))
            df_data[key][filter_applied1] = pd.to_datetime(
                df_data[key][filter_applied1].astype(
                    'int').astype('str')).dt.year

            # String check
            filter_applied2 = ((not_null_filter) & (~numeric_filter)) & (
                error_data[key][error_data[key] == correction_data[key][0]])
            df_data[key][filter_applied2] = pd.to_datetime(
                df_data[key][filter_applied2]).dt.year

            df_data[key][~(filter_applied1 | filter_applied2)] = np.NaN
        # Applying filter to entire column, example indicator category might be
        # have numbers
        elif correction_data[key][1] == 'text':
            filter_applied = not_null_filter & (~numeric_filter)
            df_data[key] = df_data[key].apply(clean_lambda)
        else:  # numeric
            if correction_data[key][0] == 'text':
                if key in index_order['value']:
                    print('TODO')
            else:
                filter_applied = not_null_filter & (~numeric_filter)
                df_data[key][filter_applied] = np.NaN

    return df_data


def lookForError(f, default, x):
    try:
        value = f(x)
    except Exception:
        value = default
    return default


def convert_df(df_data, multi_entry_dict, data_model_dict,
               value_format_value, dtypes_dict):
    '''Remaps dataframe based on relationship between columns and data model.

    Args:
        mappings ({str:[str]}): the users chosen mappings for a file column.
        relationship_dict ({str: [str]}): section of the data model mapped
        to a file column heading.
        left_over_dict ({str: [str]}): section of the data model mapped to
        the file column values.
        df_data (Dataframe): dataframe of CSV file.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        empty_unit_measure_value (str): value to use if unit
        of measure has not be mapped.

    Returns:
        new_df (Dataframe): newly formatted dataframe.
        dtypes_dict ({str:str}): stores the data-types found for each heading.
        mappings ({str:[str]}): the users chosen mappings for a file column.
    '''

    if not value_format_value:
        value_format_value = {}

    relationship_dict = multi_entry_dict['column_heading']
    left_over_dict = multi_entry_dict['column_values']
    columns = []

    new_df = pd.DataFrame(columns=df_data.columns)

    # Todo vectorise
    for col in relationship_dict:
        tmp_df = df_data.copy(deep=True)
        tmp_df[relationship_dict[col]] = col
        tmp_df[left_over_dict[col]] = tmp_df[col]

        if col in value_format_value:
            tmp_df['value_format'] = value_format_value[col]
            data_model_dict['value_format'] = ['value_format']
            dtypes_dict['value_format'] = ['text'] * \
                len(tmp_df[tmp_df.columns[0]])
        new_df = new_df.append(tmp_df)

    for col in relationship_dict:
        if relationship_dict[col] == 'date':
            data_model_dict['date'] = ['date']
            dtypes_dict[relationship_dict[col]] = [
                'date'] * len(tmp_df[tmp_df.columns[0]])
        else:
            if 'filters' not in data_model_dict['filters']:
                data_model_dict['filters'].append('filters')
            data_model_dict['filters'].remove(col)
            dtypes_dict[relationship_dict[col]] = [
                'text'] * len(tmp_df[tmp_df.columns[0]])
        data_model_dict['value'] = ['value']
        dtypes_dict[left_over_dict[col]] = dtypes_dict[col]

    return new_df.reset_index(), dtypes_dict, data_model_dict
    # filter by columns needed


def check_file_type(file_name):
    name = file_name.lower()
    if name.endswith('.csv'):
        return True, {'file_type': 'csv', 'success': 1}
    elif name.endswith('.xlsx'):
        return False, {'file_type': 'xlsx', 'success': 0,
                       'error': 'Cannot map xlsx files'}
    elif name.endswith('.json'):
        return False, {'file_type': 'json', 'success': 0,
                       'error': 'Cannot map json files'}
    else:
        return False, {'file_type': 'Unrecognised format', 'success': 0,
                       'error': 'Don\'t recognise file type'}  # .txt format??


def check_file_formatting(file_loc):
    try:
        df_data = pd.read_csv(file_loc)
    except Exception as e:
        return False, {
            'success': 0,
            'error': 'Couldn\'t read file, check start of file for text, '
                     'for malformed columns and  for gaps in data.'
        }
    # check column names if unammed give back false
    for key in df_data.columns:
        if 'Unnamed' in key:
            return False, {
                'success': 0,
                'error': 'Cannot validate, unnamed columns in data set or '
                         'unessecary text at start of file.'
            }
        else:
            nan_indexes = pd.isnull(df_data)
            # for col in df_data.ix[:,0]:

    resulting_indexes = nan_indexes.apply(
        lambda x: min(x) == max(x) and min(x), 1)
    result = len(resulting_indexes[resulting_indexes]) > 0
    if result:
        # return line number of blank lines?
        return False, {
            'success': 0,
            'error': 'Files has blank lines or text at end of the file.'
        }
    return True, {'success': 1}
    # check end of file if there is empty line and the df_
    # data lenght is longer than this line then error
    # get columns with the least amount of empty values
    # check which has the least amount


def get_line_index(line_records, line_no):
    i = 0
    for line in line_records:
        if line['Item'] == line_no:
            return i
        else:
            i += 1
    return -1

# from file_upload.models import File


if __name__ == '__main__':
    main()
