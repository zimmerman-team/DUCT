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
            df_data.to_csv(f)

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

    if request.data["type"] == "csv":
        #og_data = pd.read_csv(File.objects.get(id=file_id).file)#allow multiple files
        df_data = pd.read_csv(File.objects.get(id=file_id).file)

    if request.data["filter_toggle"]:
        #look for empty string if given or nan's
        if request.data['replace_pressed']:
            print("this is the replace value: ",request.data['replace_value'])
            df_data[request.data["filter_value"]][df_data[request.data["filter_value"]] == request.data['find_value']] = request.data['replace_value']
            with open(str(File.objects.get(id=file_id).file), 'w') as f:
                df_data.to_csv(f)
            df_data = df_data[df_data[request.data["filter_value"]] == request.data['replace_value']]
        else:
            df_data = df_data[df_data[request.data["filter_value"]] == request.data['find_value']]
           
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
        if start_pos >= len(df_data[df_data.columns[0]]) - 1:
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
    return context
    #start lines and end lines
    # newdoc_path = request.session['files'][0]
    #newdoc_name = request.session['files'][0].split("/")[-1]
    """column_headings = list(df_data.columns)
    dtypes_dict = request.data['dtypes_dict']
    dtypes_dict_file_name = FileDtypes.objects.get(file=File.objects.get(id=file_id)).dtype_name 
    print(dtypes_dict_file_name)
    with open(dtypes_dict_file_name, 'rb') as f:
        error_data = pickle.load(f)
    #error_data = request.data['missing_dtypes_list']
    #error_data = #he data each line has
    line_no = np.array([])
    pointer = []
    for i in range(len(column_headings)):#minus one for line no
        data_types = np.array([j[0] for j in error_data[i]]) # column
        indexes = np.where(data_types != dtypes_dict[column_headings[i]][0][0])
        line_no = np.append(line_no, indexes)#line_no + list(np.where(data_types == dtypes_dict[column_headings[i]][0][0]))
        #pointer.append(0)
    #line_no = np.array(line_no)
    error_line_no = np.unique(line_no) # get only line numbers that have errors # mioght need to sort array


    ##go through headings get the most common dtypes 
    #search for the lines that have the least common
    #highlight them some how  using javascript
    #define ids for html elements by combining column name with id number 'generate this list accordingly'

    #might be better to generate teh html beforehand

    #list according to ids?????


    #get dictionary of line number that have error and give columns of error
    #for i in range(len(df_data[column_headings[0]])):
    
    #if len(error_line_no) <= 200: 

    for i in error_line_no:
        i = int(i)#i float 64
        temp_list = []
        temp_error_ids = []
        for j in range(len(column_headings)):#minus one for line no
            if dtypes_dict[column_headings[j]][0][0] != error_data[j][i][0]: #error[0][0][ => column 0 line 0 value= (dtype, line_no)#this doesn't make sense
                #log line to highlight
                found_error_ids.append((str(i+1)+"_"+column_headings[j], "found " + error_data[j][i][0] + " should be " + dtypes_dict[column_headings[j]][0][0]))
                #found_error = True
            temp_list.append(df_data.iloc[i, j])
            temp_error_ids.append(str(i+1)+"_"+ column_headings[j])
        #if found_error:
        line_numbers.append(i + 1)
        data_list.append(zip(temp_list, temp_error_ids))
        #error_ids.append(temp_error_ids)
        #found_error = False

    #zip_list = zip(*[data_list, error_ids])
    zip_list = zip(line_numbers, data_list)
    context = {"df_data" : zip_list, "column_headings":column_headings, "found_error_ids" : found_error_ids}
    
    #else:
    #    error_count = len(error_line_no)
    #    list_of_errors = [] 
    #    context = {"error_count": len(error_line_no), "list of errors": list_of_errors, "newdoc_name": newdoc_name}"""

    return context
    #return render(request, 'error_correct/error_correct.html', context)
