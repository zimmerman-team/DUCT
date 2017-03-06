from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from django.db import connection,transaction
from indicator.models import *
from geodata.models import Country
from lib.converters import convert_to_JSON # check if this works
from django.conf import settings
from sqlalchemy import create_engine
from lib.tools import check_column_data, correct_data, convert_df
import numpy as np
import pandas as pd
import pickle 
import json
import datetime
import time
import os

def index(request):
    if request.method == 'POST':
        
        #check data types

        # add validation check here
        if 'dict' in request.POST:
            mappings = json.loads(request.POST['dict']) 
            mappings.pop("null", None)
            mappings.pop("unit_measure", None)#change later
            mappings.pop("validate_store", None) # remove??
            df_data = pd.read_csv(request.session['files'][0]) # change to use with multiple files
            found_dtype = []
            convert_to_dtype = []
            error_message = []
            correction_mappings = {}

            dict_name = request.session['dtypes']
            with open(dict_name, 'rb') as f:
                dtypes_dict = pickle.load(f)

            if 'empty_indicator' in mappings:
                indicator_value = mappings.pop("empty_indicator")
                mappings['indicator_id'] = ['indicator_id']
                df_data['indicator_id'] = indicator_value
                dtypes_dict[mappings['indicator_id'][0]] = ('str', 'str')
                #add indicator value as column 

            if "relationship" in mappings:
                relationship_dict = mappings.pop("relationship")
                left_over_dict = mappings.pop("left_over")

                df_data = convert_df(relationship_dict, left_over_dict, df_data, dtypes_dict) 
                #for each line in df data
            #column_check = df_data.columns# 
    
            #Validation
            for key in mappings:
                    #return HttpResponse(key)
                    if mappings[key]:#this is included incase no mapping is given

                        if not mappings[key][0] in df_data.columns:
                            temp = mappings[key][0]
                            mappings[key][0] = mappings[key][0].replace("~", " ")
                        
                        correction_mappings[mappings[key][0]] = []
                        temp_results_check_dtype, temp_found_dtype, temp_convert_dtype = check_column_data(dtypes_dict[mappings[key][0]], df_data[mappings[key][0]], key, mappings[key][0])

                        if temp_results_check_dtype != False:
                            #found_dtype.append(temp_found_dtype)
                            #convert_to_dtype.append(temp_convert_dtype)
                            correction_mappings[mappings[key][0]] = (temp_found_dtype, temp_convert_dtype) 
                        else:
                            error_message.append(mappings[key][0] + " to " + key + ", found " + temp_found_dtype + ", needed " + temp_convert_dtype + ". ")#datatype blah blah 
                        ###
            #df_data['mAP']# MISTAKE
            if len(error_message) > 0:
                #cache.clear() # check if necessary for ctrf token?   
                context = {}
                missing = []
                for heading in request.session['missing_list']: #why not just pass missing list instead of missing
                    missing.append(heading.replace(" ", "~"))
                context = {"files" : request.session['files'], "missing_headings" : missing, "remaining_headings" : request.session['remaining_headings'], "error_messages" : error_message}
                return render(request, 'manual_mapping/manual_mapping.html', context)
                #return HttpResponse(error_message)

            df_data = correct_data(df_data, correction_mappings)

            #df_data = df_data[1:len(df_data)]
            order = {}
            index_order = {}
            bulk_list = []

            #cycle through dataset and save each line
            order["file_source_id"] = request.session['files'][0] 
            instance = FileSource(file_name = order['file_source_id'])
            instance.save()
            #error  check for instance not being available

            order['file_source_id'] = instance 
            order["date_created"] = datetime.datetime.now()
            instance = Time(date_type = "YYYY")
            instance.save()
            order['date_format_id'] = instance  

            datapoint_headings = []
            for key in mappings:
                #if (not key == "file_name") or (not key == "indicator_category"):
                if mappings[key]:
                    if mappings[key][0] in df_data.columns:
                        index_order[key] = mappings[key][0]
                        datapoint_headings.append(mappings[key][0])
                    else:
                        index_order[key] = mappings[key][0].replace("~", " ") # kind of a stupid way to handle this
                        datapoint_headings.append(mappings[key][0]).replace("~", " ")

            count  = 0
            ind_dict = {}
            ind_cat_dict = {}
            ind_source_dict = {}
            ind_country_dict = {}
            unique_indicator = [] 
            unique_indicator_cat = [] 
            unique_indicator_source = [] 
            unique_country = []

            if "indicator_id" in index_order:
                unique_indicator = df_data[index_order["indicator_id"]].unique()
            if "indicator_category_id" in index_order:
                #search for indicator
                unique_indicator_cat = df_data.groupby([index_order["indicator_id"],index_order["indicator_category_id"]]).size().reset_index()
            if "source_id" in index_order:
                #get indicator if not present
                unique_indicator_source = df_data.groupby([index_order["indicator_id"],index_order["source_id"]]).size().reset_index()
            #unique_subgroup = index_order['subgroup'].unique()
            if "country_id" in index_order:
                unique_country = df_data[index_order['country_id']].unique()
            unique_lists = [unique_indicator, unique_indicator_cat, unique_indicator_source, unique_country]
            #need to fix this in case indicator missing #
            count = 0

            for unique_list in unique_lists:
                for i in range(len(unique_list)):
                    
                    if(count == 0):#indicator
                        instance = Indicator.objects.filter(id=unique_list[i]).first()
                        if not instance:
                            instance = Indicator(id = unique_list[i])
                            instance.save()
                        ind_dict[unique_list[i]] = instance
                    elif(count == 1):#indicator_cat
                        instance = IndicatorCategory.objects.filter(id=unique_list[index_order['indicator_category_id']][i], indicator = ind_dict[unique_list[index_order['indicator_id']][i]]).first()
                        if not instance:
                            instance = IndicatorCategory(id = unique_list[index_order['indicator_category_id']][i], indicator = ind_dict[unique_list[index_order['indicator_id']][i]])
                            instance.save()
                        ind_cat_dict[unique_list[index_order['indicator_id']][i] + unique_list[index_order['indicator_category_id']][i]] = instance
                    elif(count == 2):#ind_source
                        instance = IndicatorSource.objects.filter(id = unique_list[index_order['source_id']][i], indicator = ind_dict[unique_list[index_order['indicator_id']][i]]).first() 
                        if not instance:
                            instance = IndicatorSource(id = unique_list[index_order['source_id']][i], indicator = ind_dict[unique_list[index_order['indicator_id']][i]])
                            instance.save()
                        ind_source_dict[unique_list[index_order['indicator_id']][i] + unique_list[index_order['source_id']][i]] = instance
                        
                    else:#indicator_sub
                        instance = Country.objects.filter(code = unique_list[i])
                        if instance.count() > 0:
                            #instance.save()
                            ind_country_dict[unique_list[i]] = instance[0]
                        else:
                            instance = None# Country(code = unique_list[i])
                            #check = unique_list[i]
                            #try:
                            #    instance.save()
                            #    ind_country_dict[unique_list[i]] = instance
                            #except Exception as e:
                            #     #instance = None
                            ind_country_dict[unique_list[i]] = instance
                count += 1   
            count = 0
            #statement = "insert into indicator_IndicatorDatapoint (" + ', '.join(datapoint_headings) + ") values "
            #cursor = connection.cursor()
            #query=''' INSERT INTO indicator_IndicatorDatapoint 
            #        (var1) 
            #        VALUES ("indicator_id, testascbcs") '''
            #queryList=buildQueryList() 
            #here buildQueryList() represents some function to populate
            #the list with multiple records
            #in the tuple format (value1,value2,value3).
            #cursor.executemany(query,queryList)
            #transaction.commit()

            #cursor = connection.cursor()
            #statement = "insert into indicator_IndicatorDatapoint (indicator_id, date_created, file_source_id) values('test2', '%s', %s)" % (order["date_created"], order["file_source_id"].id)
            #id = cursor.execute(statement)""" 
            """user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            database_name = settings.DATABASES['default']['NAME']

            database_url = 'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(
                user=user,
                password=password,
                database_name=database_name,
            )

            engine = create_engine(database_url, echo=False)
            df_data.to_sql("indicator_indicatordatapoint1", con=engine, if_exists='append', index=False)""" #slow, really slow....
            
            for count in range(len(df_data)):
                #statement += " ("
                for key in mappings:
                    if mappings[key]:
                        if mappings[key][0] in df_data.columns:
                           order[key] = df_data[mappings[key][0]][count]
                        else:
                           order[key] = df_data[mappings[key][0].replace("~", " ")][count] # kind of a stupid way to handle this 
                        
                #instance = MeasureValue(value = order['measure_value'], value_type =order['unit_measure'], name="")
                #bulk_measure_value.append(instance)
                #del order['unit_measure'] # temporary fix
                #add measure unit
                #order['measure_value'] = instance
                #add foreign keys to indicator datapoint model

                if 'indicator_category_id' in order:
                    order['indicator_category_id'] = ind_cat_dict[order['indicator_id'] + order['indicator_category_id']] # why +??
                if 'source_id' in order:
                    order['source_id'] = ind_source_dict[order['indicator_id'] + order['source_id']]
                if 'indicator_id' in order:
                    order['indicator_id'] = ind_dict[order['indicator_id']]
                if 'country_id' in order:
                    order['country_id'] = ind_country_dict[order['country_id']]
                    #bf.d.
                
                #for key in order:
                #   statement += "'%s'," % str((order[key])).decode('utf-8')
                #statement = statement[:-1] + ") " """
                instance = IndicatorDatapoint(**order)
                bulk_list.append(instance)
            
            IndicatorDatapoint.objects.bulk_create(bulk_list)

        #delete tmp file
        os.remove(dict_name)

        #Transgender people: HIV prevalence, 
        #convert_to_JSON("Transgender people: HIV prevalence", "Transgender people: Population size estimate")#allow user to choose these
        return HttpResponseRedirect('/scatter_demo/')
    else:
        #cache.clear() # check if necessary for ctrf token?   
        context = {}
        missing = []
        dict_values = []
        for heading in request.session['missing_list']: #why not just pass missing list instead of missing
            missing.append(heading.replace(" ", "~"))
            dict_values.append(heading)

        context = {"files" : request.session['files'], "missing_headings" : missing, "remaining_headings" : request.session['remaining_headings'], "dict_values" : dict_values}
        return render(request, 'manual_mapping/manual_mapping.html', context)       
