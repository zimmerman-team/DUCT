from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from indicator.models import *
from lib.converters import convert_to_JSON
from django.conf import settings
from sqlalchemy import create_engine
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
            mappings.pop("unit_measure", None)#change later
            mappings.pop("validate_store", None) # remove??
            df_data = pd.read_csv(request.session['files'][0])
            #df_data = df_data[1:len(df_data)]
            order = {}
            index_order = {}
            bulk_list = []
            bulk_measure_value = []

            test = ""
            #cycle through dataset and save each line
            order["file_source_id"] = request.session['files'][0] 
            instance = FileSource(file_name = order['file_source_id'])
            instance.save()
            if instance.pk is None:
                return HTTPResponse("Error")
            order['file_source_id'] = instance 
            order["date_created"] = datetime.datetime.now()
            indicator_dict = {}
            index_order = {}
            instance = Time(date_type = "YYYY")
            instance.save()
            #if instance.pk is None:
            #    return HTTPResponse("Error")
            order['date_format_id'] = instance  


            #only need to create file object once
            #only create date once
            for key in mappings:
                #if (not key == "file_name") or (not key == "indicator_category"):
                if mappings[key] in df_data.columns:
                    index_order[key] = mappings[key]
                else:
                    index_order[key] = mappings[key].replace("_", " ") # kind of a stupid way to handle this

            count  = 0

            ind_dict = {}
            ind_cat_dict = {}
            ind_source_dict = {}
            #ind_subgroup_dict = {}
            ind_country_dict = {}

            unique_indicator = df_data[index_order["indicator_id"]].unique()
            unique_indicator_cat = df_data.groupby([index_order["indicator_id"],index_order["indicator_category_id"]]).size().reset_index()
            unique_indicator_source = df_data.groupby([index_order["indicator_id"],index_order["source_id"]]).size().reset_index()
            #unique_subgroup = index_order['subgroup'].unique()
            unique_country = df_data[index_order['country_id']].unique()
            unique_lists = [unique_indicator, unique_indicator_cat, unique_indicator_source, unique_country]
            for unique_list in unique_lists:
                for i in range(len(unique_list)):
                    if(count == 0):#indicator
                        instance = Indicator(id = unique_list[i])
                        instance.save()
                        ind_dict[unique_list[i]] = instance
                    elif(count == 1):#indicator_cat
                        instance = IndicatorCategory(id = unique_list[index_order['indicator_category_id']][i], indicator = ind_dict[unique_list[index_order['indicator_id']][i]])
                        instance.save()
                        ind_cat_dict[unique_list[index_order['indicator_id']][i] + unique_list[index_order['indicator_category_id']][i]] = instance
                    elif(count == 2):#ind_source
                        instance = IndicatorSource(id = unique_list[index_order['source_id']][i], indicator = ind_dict[unique_list[index_order['indicator_id']][i]])
                        instance.save()
                        ind_source_dict[unique_list[index_order['indicator_id']][i] + unique_list[index_order['source_id']][i]] = instance
                    else:#indicator_sub
                        instance = Country(id = unique_list[i])
                        instance.save()
                        ind_country_dict[unique_list[i]] = instance

                count += 1

            count = 0


            """for count in range(len(df_data)):
                #test += str(line)
                for key in mappings:
                    #if (not key == "file_name") or (not key == "indicator_category_id"):
                        if mappings[key] in df_data.columns:
                            df_data=df_data.rename(columns = {mappings[key]:key})
                            #df_data[key].astype(str)
                            #order[key] = df_data[mappings[key]][count]
                        else:
                            df_data=df_data.rename(columns = {mappings[key].replace("_", " "):key})
                           # df_data[key].astype(str)
                            #order[key] = df_data[mappings[key].replace("_", " ")][count] # kind of a stupid way to handle this 
                for name in df_data.columns:
                    if not name in mappings:
                        del df_data[name]"""
            
            
            # = df_data['measure_value'].replace('', '0')
            #df_data['measure_value'] = pd.to_numeric(df_data['measure_value'], downcast='float')
            #df_data['measure_value'].map('{:,.5f}'.format)#should be part of validation part


            """user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            database_name = settings.DATABASES['default']['NAME']

            database_url = 'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(
                user=user,
                password=password,
                database_name=database_name,
            )

            engine = create_engine(database_url, echo=False)
            df_data.to_sql("indicator_indicatordatapoint1", con=engine, if_exists='append', index=False)"""

            for count in range(len(df_data)):
                #test += str(line)
                for key in mappings:
                    if (not key == "file_name") or (not key == "indicator_category"):
                        if mappings[key] in df_data.columns:
                           order[key] = df_data[mappings[key]][count]
                        else:
                           order[key] = df_data[mappings[key].replace("_", " ")][count] # kind of a stupid way to handle this 

                #order["file_source"] = request.session['files'][0] 
                
                #can this be looped??
                #order["date_value"] = datetime.date(year=int(order["date_value"]), month=1, day=1)
                
                #temp_p , temp_c
                #put all of this in a loop
                #if

                #instance = Indicator(id = order['indicator'])
                #bulk_indicator_list.append(instance)
                """bulk_indicator_list = []
                    bulk_indicator_category = []
                    bulk_indicator_source = []
                    bulk_inidcator_subgroup = [] 
                    bulk_file_source = []
                    bulk_date_format = []
                    bulk_country = []"""
                #bulk_measure_value = []
               
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                #order['indicator'] = instance#Indicator.objects.get(pk=order['indicator'])
                
                #instance = IndicatorCategory(id = order['indicator_category'], indicator = order['indicator'])
                #bulk_indicator_category.append(instance)
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                #order['indicator_category'] = instance#IndicatorCategory.objects.get(pk=order['indicator_category'])
                
                #instance = IndicatorSource(id = order['source'], indicator = order['indicator'])
                #bulk_indicator_source.append(instance)
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                #order['source'] = instance#IndicatorSource.objects.get(pk=order['source']) 
                
                #instance = IndicatorSubgroup(id = order['subgroup'], indicator = order['indicator'])
                #bulk_inidcator_subgroup.append(instance)
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                #order['subgroup'] = instance#IndicatorSubgroup.objects.get(pk=order['subgroup']) 


                #instance = Country(id = order['country'])
                #bulk_country.append(instance)
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                #order['country'] = instance 

                #instance = MeasureValue(value = order['measure_value'], value_type =order['unit_measure'], name="")
                #bulk_measure_value.append(instance)
                #del order['unit_measure']
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                #add measure unit
                #order['measure_value'] = instance
                order['indicator_category_id'] = ind_cat_dict[order['indicator_id'] + order['indicator_category_id']]
                order['source_id'] = ind_source_dict[order['indicator_id'] + order['source_id']]
                order['indicator_id'] = ind_dict[order['indicator_id']]
                order['country_id'] = ind_country_dict[order['country_id']]
                #instance.save()
                instance = IndicatorDatapoint(**order)
                bulk_list.append(instance)
                #instance.save()
                #if instance.pk is None:
                #    return HTTPResponse("Error")
                
                #count += 1
                #order = {} not needed
            #MeasureValue.objects.bulk_create(bulk_measure_value)
            IndicatorDatapoint.objects.bulk_create(bulk_list)

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
            #new_df = pd.DataFrame()
            #'df.columns = ['a', 'b']'
            
            #for alignment in existing_mappings:
                
            #    column1, column2 = alignment.split("to") #alwats mapping from template to file  
            #    column1 = int(column1.strip()) # template column
            #    column2 = int(column2.strip()) # file column
                #new_df['new heading'] = df_file[column
                #newdf = df_data[df_file.columns[2:4]]                
            #df_new = 
            #lopp through and give column names to dataframe
       #return HttpResponse(str(count) + " len " + str(len(df_data)) + " ")
            

        #check = request.POST["check"]
        #c = request.POST.get('mapping_dict')
        #context= {'data_check' : data, "value" : value}
        #Transgender people: HIV prevalence, 
        convert_to_JSON("Transgender people: HIV prevalence", "Transgender people: Population size estimate")#allow user to choose these

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