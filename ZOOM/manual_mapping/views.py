from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from indicator.models import *
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
                    if (not key == "file_name") or (not key == "indicator_category"):
                        if mappings[key] in df_data.columns:
                            order[key] = df_data[mappings[key]][count]
                        else:
                            order[key] = df_data[mappings[key].replace("_", " ")][count] # kind of a stupid way to handle this 

                order["file_source"] = request.session['files'][0] 
                
                #can this be looped??
                #order["date"] = datetime.date(year=int(order["date"]), month=1, day=1)
                order["date_created"] = datetime.datetime.now()
                #temp_p , temp_c
                p = [None] * 10
                created = [None] * 10
                #put all of this in a loop
                instance = Indicator(id = order['indicator'])
                instance.save()
                order['indicator'] = Indicator.objects.get(pk=order['indicator'])
                
                instance = IndicatorCategory(id = order['indicator_category'], indicator = order['indicator'])
                instance.save()
                order['indicator_category'] = IndicatorCategory.objects.get(pk=order['indicator_category'])
                
                instance = IndicatorSource(order['source'], indicator = order['indicator'])
                instance.save()
                order['source'] = IndicatorSource.objects.get(pk=order['source']) 
                
                instance = IndicatorSubgroup(id = order['subgroup'], indicator = order['indicator'])
                instance.save()
                order['subgroup'] = IndicatorSubgroup.objects.get(pk=order['subgroup']) 

                instance = FileSource(file_name = order['file_source'])
                instance.save()
                order['file_source'] = instance 

                instance = Time(date_type = "YYYY")
                instance.save()
                order['date_format'] = instance 

                instance = Country(id = order['country'])
                instance.save()
                order['country'] = instance 

                instance = MeasureValue(value = order['measure_value'], value_type ="numeric", name="")
                instance.save()
                order['measure_value'] = instance

                #temp_c = False
                #temp_p  = 0

                """temp_p , temp_c = Indicator.objects.get_or_create(id = order['indicator'])
                                                                #p[0] = temp_p
                                                                created[0] = temp_C
                                                                p[1], created[1] = IndicatorCategory.objects.get_or_create(id = order['indicator_category'], indicator = order['indicator'])
                                                                p[2], created[2] = IndicatorSource.objects.get_or_create(id = order['indicator_source'], indicator = order['indicator'])
                                                                p[3], created[3] = IndicatorSubgroup.objects.get_or_create(id = order['indicator_subgroup'], indicator = order['indicator'])
                                                                p[4], created[4] = FileSource.objects.get_or_create(id = order['FileSource'], file_name = order['file_name'])
                                                                p[5], created[5] = Time.objects.get_or_create(id = "YYYY")
                                                                p[6], created[6] = Country.objects.get_or_create(id = order['country'])
                                                                p[7], created[7] = MeasureValue.objects.get_or_create(value = order['measure_value'], value_type ="numeric", name="")
                                                """
                #for ob, check in p, c:
                #    if check:
                #        ob.save()
                #p[6], created[6] = Organisation.objects.get_or_create(id = order['Organisation'])
                #p[6], created[6] = Sector.objects.get_or_create(id = order['sector'])
                #p[6], created[6] = Region.objects.get_or_create(id = order['region'])
                #p[4], created[4] = Time.objects.get_or_create(id = "YYYY")

                #instance.save()
                instance = IndicatorDatapoint(**order)
                instance.save()
                count += 1
                order = {}
            data = IndicatorDatapoint.objects.all()

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
        return HttpResponseRedirect('/scatter_demo/')
        #return HttpResponseRedirect(reverse('../scatter_demo'))
        #return render(request, 'manual_mapping/output.html', context) #render(request, 'manual_mapping/manual_mapping.html', context)    
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