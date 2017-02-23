from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from indicator.models import IndicatorDatapoint
from lib.converters import convert_spreadsheet
from lib.tools import check_column_data, identify_col_dtype
from geodata.importer.country import CountryImport
from geodata.models import get_dictionaries
from .models import File
from .forms import DocumentForm
import json
import numpy as np
import pandas as pd

#@ensure_csrf_cookie
def index(request):
    context = {}
    request.session['test'] = "test" # create test user session if it doesnt exist
    #cache.clear() #???
    #ci = CountryImport()
    ##ci.update_country_center()
    #ci.update_polygon()
    #ci.update_regions()
    #country_data.update_polygon()
    #CountryImport.update_polygon()
    
    if request.method == 'POST':

        form = DocumentForm(request.POST, request.FILES)
        if request.session['checked_error']:
            #get from seetion
            #makes changes in csv file
            newdoc = request.session['files']#use loop here to loop through file/locations

            if 'dict' in request.POST:#user has corrected csv file
                df_data = pd.read_csv(newdoc[0])
                corrections = json.loads(request.POST['dict']) 
                
                for line_no in corrections:
                    for i in range(1, len(corrections[line_no])): 
                        df_data.iloc[int(line_no) - 1, i] = corrections[line_no][i] #line[0]-1 cause started at 1 for visual design 
                
                df_data.to_csv(newdoc[0],  mode = 'w', index=False)
            request.session['checked_error'] = False
        else:
            newdoc = upload(request)

        return validate(request, newdoc)
    else:
        form = DocumentForm() # Allow multiple csv entries
        documents = File.objects.all() #load templates only
        template = loader.get_template('validate/input.html')
        validate_form = False
        request.session['checked_error'] = False
        context = {
          'validate': validate_form,
          'documents': documents,
          'form' : form}
        return render(request, 'validate/input.html', context)
   
        
#need to clean this up
def upload(request):
    newdoc = []
    count = 0
    #save uploaded files # look for HXL tags
    for filename, file in request.FILES.iteritems():
        #name = request.FILES[filename].name
        instance = File(file = request.FILES[filename])
        instance.save()
        newdoc.append(instance.get_file_path())
        count += 1

    #return render(request, 'validate/asinput.html', {})
    return newdoc

def validate(request, newdoc):
    validate_form = True
    count = 0
    overall_count = 0
    
    missing_mapping = [] #change name -> doesn't make sense 
    remaining_mapping = []#also doesn't make sense any more
    missing_datatypes = []
    found_mapping = []
    mapping = [] # what does this mean????
    validation_results = []
    dtypes_list = []
    error_lines = []

    dtypes_dict = {}
    headings_template = {}
    headings_file = {}

    count = 0
    #loop here for multiple files
    df_file = pd.read_csv(newdoc[0])#.get_file_path())
    file_heading_list = df_file.columns
    #sample_amount = len(df_file[file_heading_list[0]]) # might be too big, might take too long
    template_heading_list = []
    
    #Get datapoint headings
    for field in IndicatorDatapoint._meta.fields:
        template_heading_list.append(field.name)#.get_attname_column())
    
    template_heading_list = template_heading_list[4:len(template_heading_list)]#skip first four headings as irrelevant to user input
    template_heading_list.append("unit_measure") #needed? 
    
    #count = 0# not sure if this is still needed, might need for matches
    dicts = get_dictionaries()#get dicts for country
    for heading in file_heading_list:
        headings_file[heading] = count
        prob_list, error_count = identify_col_dtype(df_file[heading], heading, dicts)
        dtypes_dict[heading] = prob_list 
        
        error_lines.append(error_count)
        validation_results.append(df_file[heading].isnull().sum())
        dtypes_list.append(prob_list) 
        #count += 1

    count = 0 #count matching
    overall_count = len(template_heading_list)

    for key in template_heading_list:
      remaining_mapping.append(key)
    
    files = []
    files_id = []
    files.append(newdoc[0])#.get_file_path())   
    zip_list = zip(file_heading_list, dtypes_list, validation_results)#zip(found_mapping, mapping, data_types, validation_on_types)
    missing_mapping = list(headings_file.keys())
    
    #check this, see if these are relevant 
    request.session['missing_dtypes_list'] = error_lines #change name # error per column, error[0][0] => 1st column 1st line
    request.session['found_mapping'] = []#file_heading_list#zip_list
    request.session['missing_list'] = missing_mapping#change name -> silly
    request.session['files'] = files
    request.session['dtypes'] = dtypes_dict
    #request.session['template_file'] = template_file
    request.session['remaining_headings'] = remaining_mapping
    
    context = {'validate': validate_form, 'mapped' : count, "no_mapped" : overall_count - count, "found_list": zip_list, "missing_list" : remaining_mapping, "files" : files[0]}#reorganise messy
    #output need to pass allignments of mapped headings
    return render(request, 'validate/input.html', context)


def get_file_type(django_file):
    name = django_file.name.lower()
    if name.endswith('.json'):
        return 'json'
    elif name.endswith('.xlsx'):
        return 'xlsx'
    elif name.endswith('.csv'):
        return 'csv'
    else:
        first_byte = django_file.read(1)
        if first_byte in [b'{', b'[']:
            return 'json'
        else:
            raise UnrecognisedFileType
