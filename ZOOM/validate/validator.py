from django.conf import settings
import os
import pickle
import uuid
import numpy as np
import pandas as pd

from indicator.models import IndicatorDatapoint
from lib.tools import identify_col_dtype
from file_upload.models import File
from file_upload.models import FileDtypes
from geodata.importer.country import CountryImport
from geodata.models import get_dictionaries


def validate(file_id):
    # file_id = file_id
    #tmp
    print(file_id)
    newdoc = ['Item'] 
    validate_form = True
    count = 0
    overall_count = 0

    #change name -> doesn't make sense
    missing_mapping = [] 
    #also doesn't make sense any more 
    remaining_mapping = []
    missing_datatypes = []
    found_mapping = []
    # what does this mean????
    mapping = [] 
    validation_results = []
    dtypes_list = []
    error_lines = []
    summary_results = []
    summary_indexes = []

    dtypes_dict = {}
    headings_template = {}
    headings_file = {}

    count = 0
    newdoc[0] = str(File.objects.get(id=file_id).file)

    #loop here for multiple files
    #.get_file_path())
    df_file = pd.read_csv(newdoc[0])
    file_heading_list = df_file.columns

    # might be too big, might take too long
    #sample_amount = len(df_file[file_heading_list[0]]) 

    template_heading_list = []
    
    #Get datapoint headings
    for field in IndicatorDatapoint._meta.fields:
        template_heading_list.append(field.name)#.get_attname_column())
    
    #skip first four headings as irrelevant to user input
    template_heading_list = template_heading_list[4:len(template_heading_list)]

    #template_heading_list.append("unit_measure") #needed? 
    
    #get dicts for country
    dicts, _ = get_dictionaries()
    for heading in file_heading_list:
        headings_file[heading] = count
        prob_list, error_count = identify_col_dtype(df_file[heading], heading, dicts)
        dtypes_dict[heading] = prob_list       
        error_lines.append(error_count)
        validation_results.append(df_file[heading].isnull().sum())
        dtypes_list.append(prob_list)
        column_detail = df_file[heading].describe()
        summary_results.append(np.array(column_detail).astype('str'))
        summary_indexes.append(list(column_detail.index))


    #count matching
    count = 0 
    overall_count = len(template_heading_list)

    for key in template_heading_list:
      remaining_mapping.append(key)
    
    files = []
    files_id = []
    files.append(newdoc[0])
    #summary_results won't zip correctly
    zip_list = zip(file_heading_list, dtypes_list, validation_results)
    missing_mapping = list(headings_file.keys())
    
    path = os.path.join(os.path.dirname(settings.BASE_DIR), 'ZOOM/media/tmpfiles')
    dict_name = path +  "/" + str(uuid.uuid4()) + ".txt"
    with open(dict_name, 'w') as f:
        pickle.dump(error_lines, f) 
    print("dict name:  ", dict_name)
    print("File:  ", File.objects.get(id=file_id))
    FileDtypes(dtype_name=dict_name, file=File.objects.get(id=file_id)).save()

    print("dtypes_dict", dtypes_dict)
    context = {
        'success': 1, 
        'mapped' : count, 
        "no_mapped" : overall_count - count, 
        "found_list": zip_list, 
        "summary":zip(summary_indexes, summary_results), 
        "missing_list" : remaining_mapping, 
        "files" : files[0], 
        "dtypes_dict" : dtypes_dict
    }

    # print(len(summary_results));
    # print(len(validation_results));

    #output need to pass allignments of mapped headings
    return context
