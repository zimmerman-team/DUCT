from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from file_upload.models import File, FileDtypes
import pickle
import json
import numpy as np
import pandas as pd


def get_errors(request):
    print("getting errors")
    file_id = request.data['file_id']
    dtypes_dict = request.data['dtypes_dict']
    start_pos = request.data['start_pos']
    end_pos = request.data['end_pos']

    """  remove this dependency, store headings in dict for error data"""
    file_name = File.objects.get(id=file_id).file
    df_data = pd.read_csv(file_name)
    column_headings = df_data.columns
    """                         """

    dtypes_dict_file_name = FileDtypes.objects.get(file=File.objects.get(id=file_id)).dtype_name 
    
    with open(str(dtypes_dict_file_name), 'rb') as f:
        error_data = pickle.load(f)
    
    errors = {}
    counter = 0

    for i in column_headings:#minus one for line no
        #g = lambda x: if x[0] == 
        indexes = [x for x in error_data[counter][start_pos:end_pos] if x[0] != dtypes_dict[i][0][0]] #filter(, error_data[i][start_pos:end_pos])#np.where(data_types != dtypes_dict[column_headings[i]][0][0])
        print("required ", dtypes_dict[i][0][0], " what we have ", error_data[counter][start_pos:end_pos])
        print(indexes)
        errors[i] =  indexes
        counter += 1
    print(errors)

    temp_error_message = {}
    for i in errors:
        for j in errors[i]:#minus one for line no
            message = ("Found " + j[0] + ", should be " + dtypes_dict[i][0][0])
            temp_error_message[''.join([str(j[1]),"|",i])] = (message)

    context = {"error_messages": temp_error_message}
    print(context)

    return context

def update(request):
    if request.data['type'] == "csv":
        print("Request ", request.data)
        file_id = request.data['file_id']
        print("File location ", File.objects.get(id=file_id).file)
        df_data = pd.read_csv(File.objects.get(id=file_id).file)
        row_data = request.data['row']
        row_data.pop('index', None)
        line_no = row_data.pop('line no.')


        for i in row_data:
            print('heading: ', i)
            print("replacing ", df_data[i][line_no], "  ", row_data[i])
            df_data[i][line_no] = row_data[i]
        
        with open(str(File.objects.get(id=file_id).file), 'w') as f:
            df_data.to_csv(f, index=False)

    return {"success" : 1}

def error_correction(request):
    print("----------------------checking data-------------------------")
    print(request.data)
    line_numbers = []
    data_list = []
    found_error_ids = []
    error_ids = []
    found_error = False
    file_id = request.data["file_id"]
    start_pos = request.data["start_pos"]
    end_pos = request.data["end_pos"]
    apply_filter = ""

    if request.data["type"] == "csv":
        #og_data = pd.read_csv(File.objects.get(id=file_id).file)#allow multiple files
        df_data = pd.read_csv(File.objects.get(id=file_id).file)

        if request.data["filter_toggle"]:
            #look for empty string if given or nan's

            if request.data["find_value"] == "nan":
                apply_filter = df_data[request.data["filter_value"]].isnull()
            else:    
                apply_filter = df_data[request.data["filter_value"]] == request.data['find_value']

            if request.data['replace_pressed']:
                print("this is the replace value: ",request.data['replace_value'])
                
                df_data[request.data["filter_value"]][apply_filter] = request.data['replace_value']
                with open(str(File.objects.get(id=file_id).file), 'w') as f:
                    df_data.to_csv(f, index=False)
                df_data = df_data[df_data[request.data["filter_value"]] == request.data['replace_value']]
            else:
                df_data = df_data[apply_filter]
               
        #if filter apply it

        #replace everything in the column 

        output_list  = []
        org_data = df_data.copy(deep=True)
        org_data['line_no'] = org_data.index.values
        org_data = org_data.reset_index()
        df_data = df_data.reset_index()
        #print(df_data)
        counter = 0
        print("start pos ", start_pos, " end pos ", end_pos, "length ", len(df_data[df_data.columns[0]]) - 1)
        start = start_pos
        for start_pos in range(start, end_pos):
            if start_pos > len(df_data[df_data.columns[0]]) - 1:
                break
            temp_dict={}
            temp_dict = {"line no.": org_data['line_no'][start_pos]}
            for column in df_data.columns:
                temp_dict[column] = str(df_data[column][start_pos])
                #print(df_data.index.get_loc(df_data[column].iloc[start_pos].name))
            output_list.append(temp_dict)
            counter = counter + 1
            print("check " ,counter, ' start_pos ', start_pos )

        print("counter ", counter ," length of dataframe ", len(str(df_data[df_data.columns[0]])))
        #context = {"table": output_list, "errors": [], "error_message": [], "missing_value": []}
        context = {"data_table": json.dumps(output_list), "total_amount": len(df_data[df_data.columns[0]]) }#added json dumps, front end couldn't read original format
        print("CONTEXT, ", context)

    else:
        print("type database")
        #type = database
        #filter by id

        #if filter toggle
            #check for nan
            #replace all filter all
            #use replace

        #for each in filter get data

    return context