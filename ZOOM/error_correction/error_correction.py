from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from file_upload.models import File, FileDtypes
from lib.common import get_data, get_dtype_data
import pickle
import json
import numpy as np
import pandas as pd

def error_correction(request):
    """Gets data needed for error correction."""

    print("Getting Error Correction Data")
    file_id = request.data["file_id"]
    start_pos = request.data["start_pos"]
    end_pos = request.data["end_pos"]
    apply_filter = ""

    ###Future: if type is not csv then error correction being performed on data in data base
    if request.data["type"] == "csv":
        df_data = pd.read_csv(File.objects.get(id=file_id).file)

        if request.data["filter_toggle"]:
        
            if request.data["find_value"] == "nan":
                apply_filter = df_data[request.data["filter_value"]].isnull()
            else:    
                apply_filter = df_data[request.data["filter_value"]] == request.data['find_value']

            if request.data['replace_pressed']:
                df_data[request.data["filter_value"]][apply_filter] = request.data['replace_value']
                update_data(File.objects.get(id=file_id).file, df_data)

                df_data = df_data[df_data[request.data["filter_value"]] == request.data['replace_value']]
            else:
                df_data = df_data[apply_filter]
               
        output_list  = []
        org_data = df_data.copy(deep=True)
        org_data['line_no'] = org_data.index.values
        org_data = org_data.reset_index()
        df_data = df_data.reset_index()
        counter = 0
        start = start_pos
        
        for start_pos in range(start, end_pos):
            if start_pos > len(df_data[df_data.columns[0]]) - 1:
                break
            
            temp_dict={}
            temp_dict = {"line no.": org_data['line_no'][start_pos]}

            for column in df_data.columns:
                temp_dict[column] = str(df_data[column][start_pos])
            
            output_list.append(temp_dict)
            counter = counter + 1
            
        context = {"data_table": json.dumps(output_list), "total_amount": len(df_data[df_data.columns[0]]) }#added json dumps, front end couldn't read original format
    else:
        print("not csv")
    
    return context


def get_errors(request):
    """Gets data that does not match the most probable data type found for each column."""
    
    errors = {}
    line_nos = {}
    file_id = request.data['file_id']
    start_pos = request.data['start_pos']
    end_pos = request.data['end_pos']
    df_data = get_data(file_id)
    column_headings = df_data.columns
    error_data, dtypes_dict = get_dtype_data(file_id)
    line_no_selection = np.array(range(start_pos, end_pos))

    for i in column_headings:#minus one for line no 
        indexes = [x for x in error_data[i][start_pos:end_pos] if (x != dtypes_dict[i][0][0] and (not dtypes_dict[i][0][0] == "blank"))] 
        #filter(, error_data[i][start_pos:end_pos])#np.where(data_types != dtypes_dict[column_headings[i]][0][0])
        line_no_filter = [True if x != dtypes_dict[i][0][0] else False for x in error_data[i][start_pos:end_pos]]
        errors[i] =  indexes
        line_nos[i] = line_no_selection[line_no_filter]
    
    print("Errors")
    print(errors)
    print("Line filter")
    print(line_no_filter)

    temp_error_message = {}
    
    for i in errors:
        counter = 0
        for j in errors[i]:#minus one for line no
            message = ("Found " + j + ", should be " + dtypes_dict[i][0][0])
            line_no = str(line_nos[i][counter])
            temp_error_message[''.join([line_no,"|",i])] = (message)
            counter += 1

    context = {"error_messages": temp_error_message}
    print(context)

    return context


def update(request):
    """Updates cell that user edits."""

    if request.data['type'] == "csv":
        file_id = request.data['file_id']
        df_data = get_data(file_id)
        row_data = request.data['row']
        row_data.pop('index', None)
        line_no = row_data.pop('line no.')

        for i in row_data:
            df_data[i][line_no] = row_data[i]
        
        update_data(File.objects.get(id=file_id).file, df_data)

    return {"success" : 1}

def update_data(file_loc, df_data):
    """Updates data at location file_loc"""
    with open(str(file_loc), 'w') as f:
        df_data.to_csv(f, index=False)
      
