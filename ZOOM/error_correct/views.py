from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import pickle
import numpy as np
import pandas as pd

#@ensure_csrf_cookie
def index(request):

    #check if error_counter exists
    #get data
    #rpelace old csv
    line_numbers = []
    data_list = []
    found_error_ids = []
    error_ids = []
    found_error = False 
    #only show rows where values are missing
    #only show rows where data types a re different
    #for heading in column_headings:
    """for i in range(len(df_data.index)):#takes too long
                    temp_list = []
                    for j in range(len(column_headings)):#minus one for line no
                        temp_list.append(df_data.iloc[i, j])
                    line_numbers.append(i+1)
                    data_list.append(temp_list)
                context= {"df_data" : zip(line_numbers, data_list), "column_headings":column_headings}"""

    #list(df_file[heading].isnull()) # out put and highlight bad values
    #go with the majority
    df_data = pd.read_csv(request.session['files'][0])#allow multiple files
    print request.session['files'][0]
    # newdoc_path = request.session['files'][0]
    newdoc_name = request.session['files'][0].split("/")[-1]
    print newdoc_name
    column_headings = list(df_data.columns)
    request.session['checked_error'] = True
    dict_name = request.session['dtypes']
    with open(dict_name, 'rb') as f:
        dtypes_dict = pickle.load(f)
    error_data = request.session['missing_dtypes_list']
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
    
    if len(error_line_no) <= 200: 

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
        context= {"df_data" : zip_list, "column_headings":column_headings, "found_error_ids" : found_error_ids, "newdoc_name": newdoc_name}
    else:
        error_count = len(error_line_no)
        list_of_errors = [] 
        context = {"error_count": len(error_line_no), "list of errors": list_of_errors, "newdoc_name": newdoc_name}

    return render(request, 'error_correct/error_correct.html', context)

def test(request):
    context = {}
    return render(request, 'error_correct/test.html', context)