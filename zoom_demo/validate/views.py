from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import File
import csv
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
#from myproject.myapp.models import Document
from .forms import DocumentForm
from .models import File
from zoom_demo.lib.converters import convert_spreadsheet
from zoom_demo.lib.tools import check_column_data
import numpy as np
import pandas as pd

#@ensure_csrf_cookie
def index(request):
    context = {}
    request.session['test'] = "test" # create test user session if it doesnt exist
    cache.clear() #???


    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if request.POST.has_key("upload"):#True: #form.is_valid(): change!!!!
            return upload(request)
        else:#validate
            return validate(request)
    else:
        form = DocumentForm() # Allow multiple csv entries
        documents = File.objects.all() #load templates only
        template = loader.get_template('validate/input.html')
        validate_form = False
        context = {
          'validate': validate_form,
          'documents': documents,
          'form' : form}
        return render(request, 'validate/input.html', context)
   
        
def upload(request):
    newdoc = []
    count = 0

    for filename, file in request.FILES.iteritems():
        #name = request.FILES[filename].name
        newdoc.append(File(file = request.FILES[filename]))
        newdoc[count].save()
        count += 1

    form = DocumentForm() # Allow multiple csv entries
    documents = File.objects.all() #load templates only
    template = loader.get_template('validate/input.html')
    validate_form = False
    context = {
       'validate': validate_form,
       'documents': documents,
       'form' : form}
    
    return render(request, 'validate/input.html', context)

def validate(request):
  
    validate_form = True
    #exampleFile = open(settings.MEDIA_ROOT + "/" + request.POST['file_template'])#fix this
    headings_template = {}
    headings_file = {}
    count = 0 #count matching
    overall_count = 0
    missing_mapping = []  
    remaining_mapping = []
    missing_datatypes = []
    found_mapping = []
    mapping = []
    validation_on_types = []
    data_types = []


    if not request.POST.has_key('file_template'):
        return HttpResponse("Need to select template for validation")
    template_file = request.POST['file_template']
    
    files = request.POST.getlist('files[]')
    if len(files) < 1:
        return HttpResponse("Need to select at least one csv file for mapping") # use better error handling

    df_template = pd.read_csv(template_file)
    template_heading_list = df_template.columns

    #loop here for multiple files
    df_file = pd.read_csv(files[0]) 
    file_heading_list = df_file.columns
    #with open(template_file, 'rb') as f:#use loop for this
    #   reader = csv.reader(f)
    #   template_file_content  = pd.Series(list(reader)[1:])
    

    for heading in template_heading_list:
       headings_template[heading] = count
       count += 1 #using count for mapping

    count = 0
    #apply loop here for headings
    #count = 0
    #with open(files[0], 'rb') as f2:
    #   reader = csv.reader(f2)
    #   file_heading_list = list(reader)[0]

    for heading in file_heading_list:
       headings_file[heading] = count
       count += 1

    count = 0 #count matching
    overall_count = len(template_heading_list)

    for key in template_heading_list:
      if key in headings_file:
        found_mapping.append(key)
        mapping.append(str(headings_template[key]) + " to " + str(headings_file[key]))
        headings_file.pop(key, None)
        #if validation false then add to missing column
        validation_on_column, dtype_template, dtype_file = check_column_data(df_template[key], df_file[key])
        validation_on_types.append(validation_on_column)
        data_types.append((dtype_template, dtype_file))
        #check data_types
        #data_types.append(key)
        #check data_types_check
        count += 1
        
      else:
        remaining_mapping.append(key)
       
    zip_list = zip(found_mapping, mapping, data_types, validation_on_types)
    missing_mapping = list(headings_file.keys())

    request.session['found_mapping'] = zip_list
    request.session['missing_list'] = missing_mapping
    request.session['files'] = files
    request.session['template_file'] = template_file
    request.session['remaining_headings'] = remaining_mapping 
    
    context = {'validate': validate_form, 'mapped' : count, "no_mapped" : overall_count - count, "found_list": zip_list, "missing_list" : remaining_mapping, "template_file" : template_file, "files" : files[0]}
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
