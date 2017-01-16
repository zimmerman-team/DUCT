from django.http import HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from zoom_demo.validate.models import Store
#from zoom_demo.lib.tools import check_column_type
import numpy as np
import pandas as pd
import json
import datetime
import time

def index(request):
    #return HTTPResponse("Anseo anois")
    if request.method == 'POST':
        #context = {"files" : request.session['files'], "missing_headings" : request.session['missing_list'], "remaining_headings" : request.session['remaining_headings']}
        check = "Nothing"
        if 'dict' in request.POST:
            mappings = json.loads(request.POST['dict']) 
            mappings.pop("null", None)
            mappings.pop("validate_store", None) # remove??
            df_data = pd.read_csv(request.session['files'][0])
            #df_data = df_data[1:len(df_data)]
            order = {}

            #cycle through dataset and save each line
            count = 0
            for line in df_data:
                for key in mappings:
                    if (not key == "file_source") or (not key == "indicator_type"):
                        if mappings[key] in df_data.columns:
                            order[key] = df_data[mappings[key]][count]
                        else:
                            order[key] = df_data[mappings[key].replace("_", " ")][count] # kind of stupid way to handle this 

                order["file_source"] = request.session['files'][0] 
                order["indicator_type"] = "TBD"
                order["date"] = datetime.date(year=int(order["date"]), month=1, day=1)
                order["date_created"] = datetime.datetime.now()
                instance = Store(**order)
                instance.save()
                count += 1
                order = {}
            data = Store.objects.all()

            if instance.pk is None:
                value = True
            else:
                value = False
            #count = 3
            #for key in mappings:
            #    order[count] = mappings[key]
            #    count += 1
            #found_headings = df_data.ix[:,0]# headings of template
            #found_mappings = df_data.ix[:,1]
            #files = request.session['files']
            #for field in Store._meta.fields:
            #    template_heading_list.append(field.name)
            #template_file = request.session['template_file']   
            #df_template = pd.read_csv(template_file)
            #df_file = pd.read_csv(files[0])
            #column = []
            new_df = pd.DataFrame()
            #'df.columns = ['a', 'b']'
            
            #for alignment in existing_mappings:
                
            #    column1, column2 = alignment.split("to") #alwats mapping from template to file  
            #    column1 = int(column1.strip()) # template column
            #    column2 = int(column2.strip()) # file column
                #new_df['new heading'] = df_file[column
                #newdf = df_data[df_file.columns[2:4]]                
            #df_new = 
            #lopp through and give column names to dataframe


        #check = request.POST["check"]
        #c = request.POST.get('mapping_dict')
        context= {'data_check' : data, "value" : value}
        return render(request, 'manual_mapping/output.html', context) #render(request, 'manual_mapping/manual_mapping.html', context)    
    else:
        cache.clear() # check if necessary for ctrf token?   
        context = {}
        #request.session['found_mapping'] = zip_list
        #request.session['missing_list'] = missing_mapping
        #request.session['files'] = files
        missing = []
        for heading in request.session['missing_list']:
            missing.append(heading.replace(" ", "_"))
        context = {"files" : request.session['files'], "missing_headings" : missing, "remaining_headings" : request.session['remaining_headings']}
        return render(request, 'manual_mapping/manual_mapping.html', context)       