from lib.common import get_file_data, get_dtype_data, save_validation_data, get_dictionaries
from lib.tools import update_cell_type, identify_col_dtype, get_prob_list
from metadata.models import File
import json
import numpy as np

def error_correction(request):
    """Gets data needed for error correction."""

    file_id = request.data["file_id"]
    start_pos = request.data["start_pos"]
    end_pos = request.data["end_pos"]
    
    ###Future: if type is not csv then error correction being performed on data in data base
    if request.data["type"] == "csv":
        df_data = get_file_data(file_id)
        df_columns = df_data.columns
        
        if request.data["filter_toggle"]:      
            df_data = find_and_replace(df_data, request)
        if request.data["error_toggle"]:
            df_data = filter_for_errors(df_data, request)
            
        output_list  = []
        org_data = df_data.copy(deep=True)
        org_data['line_no'] = org_data.index.values
        org_data = org_data.reset_index()
        df_data = df_data.reset_index()
        counter = 0
        total_amount = 0
        start = start_pos
        
        if len(df_data.columns) > 1:#more columns than just index
            total_amount = len(df_data[df_data.columns[0]])
            for start_pos in range(start, end_pos):
                if start_pos > len(df_data[df_data.columns[0]]) - 1:
                    break
                
                temp_dict={}
                temp_dict = {"line no.": org_data['line_no'][start_pos]}

                for column in df_data.columns:
                    temp_dict[column] = str(df_data[column][start_pos])
                
                output_list.append(temp_dict)
                counter = counter + 1
         
        context = {"data_table": json.dumps(output_list), "total_amount": total_amount, "columns": df_columns}#added json dumps, front end couldn't read original format
    else:
        print("not csv")
    
    return context


def find_and_replace(df_data, request):
    """Searches for a value and replaces if indicated"""
    file_id = request.data['file_id']
    heading = request.data["filter_value"]
    
    if request.data["find_value"] == "nan":
        filter_applied = df_data[heading].isnull()
    else: 
        temp = df_data[heading]
        temp = temp.astype("str").str.lower()  
        filter_applied = (temp == str(request.data['find_value']).lower()) 
        
    if request.data['replace_pressed']:
        df_data[heading][filter_applied] = request.data['replace_value']
        column_values = df_data[heading][filter_applied]
        
        if len(column_values) > 0:
            error_data, dtypes_dict = get_dtype_data(file_id)
            dicts, _ = get_dictionaries()
            temp_prob_list, temp_error_counter = identify_col_dtype(column_values, heading, dicts)
            error_data[heading][filter_applied] = temp_error_counter
            dtypes_dict[heading] = get_prob_list(error_data[heading])
            save_validation_data(error_data, file_id, dtypes_dict)
            update_data(File.objects.get(id=file_id).file, df_data)
        df_data = df_data[df_data[heading] == request.data['replace_value']]
    else:
        df_data = df_data[filter_applied]
    return df_data


def filter_for_errors(df_data, request):
    filter_column = request.data['error_filter_value']
    error_data, dtypes_dict = get_dtype_data(request.data['file_id'])
    errors, line_nos = check_dtypes(error_data, dtypes_dict, [filter_column], request.data["start_pos"], request.data["end_pos"])
    return df_data[line_nos[filter_column]]
    

#Need to apply optimisation here, put filter here
def check_dtypes(error_data, dtypes_dict, column_headings, start_pos=0, end_pos=0):
    """Check cells against the most popular choice"""
    errors = {}
    line_nos = {}

    ###Future: Optimise based on amount needed
    if end_pos == 0:
        end_pos = len(error_data[column_headings[0]])
    
    for i in column_headings:#minus one for line no
        if (not dtypes_dict[i][0][0] == "blank"):
            filter_applied = (error_data[i] != dtypes_dict[i][0][0])
            indexes = error_data[i][filter_applied]#[x for x in error_data[i] if (x != dtypes_dict[i][0][0] and (not dtypes_dict[i][0][0] == "blank"))]#use map
            errors[i] =  indexes
            line_nos[i] = filter_applied
        else:
            errors[i] = []
            line_nos[i] = []
    return errors, line_nos

#should combine with error_correction to optimise?
def get_errors(request):
    """Gets data that does not match the most probable data type found for each column."""
    
    temp_error_message = {}
    file_id = request.data['file_id']
    start_pos = request.data['start_pos']
    end_pos = request.data['end_pos']
    df_data = get_file_data(file_id)
    column_headings = df_data.columns
    error_data, dtypes_dict = get_dtype_data(file_id)
    errors, line_nos = check_dtypes(error_data, dtypes_dict, column_headings)
    selection = np.array(range(0, len(error_data[column_headings[0]])))
    amount = end_pos - start_pos
    
    for i in errors:

        if len(errors[i]) > 0:
            counter = 0
            line_no_selection = selection[line_nos[i]]#[start_pos:end_pos]
            errors_selection = errors[i]#[start_pos:end_pos]

            for j in errors_selection:#minus one for line no
                message = ("Found a " + j + " value instead of the most populous value " + dtypes_dict[i][0][0] + ".")
                line_no = str(line_no_selection[counter])
                temp_error_message[''.join([line_no,"|",i])] = (message)
                counter += 1

    context = {"error_messages": temp_error_message}
    return context


def update(request):
    """Updates cell that user edits."""
    if request.data['type'] == "csv":
        file_id = request.data['file_id']
        df_data = get_file_data(file_id)
        error_data, dtypes_dict = get_dtype_data(file_id)
        
        if 'changeHeader' in request.data:
            count = 2
            tmp = request.data['header_value']
            while tmp in df_data.columns:
                tmp = request.data['header_value'] + str(count)
                count += 1
            request.data['header_value'] = tmp
            df_data = df_data.rename(columns={request.data['header_tobe_changed']: request.data['header_value']})
            dtypes_dict[request.data['header_value']] = dtypes_dict[request.data['header_tobe_changed']]
            dtypes_dict.pop(request.data['header_tobe_changed'], None) 
            error_data[request.data['header_value']] = error_data[request.data['header_tobe_changed']]
            error_data.pop(request.data['header_tobe_changed'], None) 
        else:
            heading = request.data['column']
            row_data = request.data['row']
            row_data.pop('index', None)
            line_no = row_data.pop('line no.')
            df_data[heading][line_no] = row_data[heading]
            
            prob_list, error_count = update_cell_type(df_data[heading][line_no], error_data[heading], line_no, heading) 
            dtypes_dict[heading] = prob_list
            error_data[heading] = error_count

        save_validation_data(error_data, file_id, dtypes_dict)
        update_data(File.objects.get(id=file_id).file, df_data)

    return {"success" : 1}

def delete_data(request):
    """Deletes data based on request"""
    file_id = request.data['file_id']
    df_data = get_file_data(file_id)
    row_keys = list(map(int, request.data['row_keys']))
    df_data = df_data.drop(df_data.index[row_keys])
    df_data = df_data.reset_index(drop=True)
    error_data, dtypes_dict = get_dtype_data(file_id)
    error_data, dtypes_dict = remove_entries(error_data, dtypes_dict, row_keys)
    save_validation_data(error_data, file_id, dtypes_dict)
    update_data(File.objects.get(id=file_id).file, df_data)
    return {"success" : 1}

def remove_entries(error_data, dtypes_dict, row_keys):
    """Remove rows from error_data and dtypes_dict"""
    for i in error_data:
        error_data[i] = error_data[i].drop(error_data[i].index[row_keys]).reset_index(drop=True)#np.delete(np.array(error_data[i]), row_keys).reset_index()
        dtypes_dict[i] = get_prob_list(error_data[i])
    return error_data, dtypes_dict

def update_data(file_loc, df_data):
    """Updates data at location file_loc"""
    with open(str(file_loc), 'w') as f:
        df_data.to_csv(f, index=False)
      
