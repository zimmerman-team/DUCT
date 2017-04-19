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
from django.http import Http404
from validate.models import File
import numpy as np
import pandas as pd
import pickle 
import json
import datetime
import time
import os


def manual_mapper(data):
	if 'dict' in data:
		mappings = data['dict']#json.loads(data['dict']) 
		mappings.pop("null", None)#not needed for api call
		mappings.pop("validate_store", None) # not needed for api call
		file_id = str(File.objects.get(id=data['file_id']).file)
		df_data = pd.read_csv(file_id) # change to use with multiple files
		found_dtype = []
		convert_to_dtype = []
		error_message = []
		correction_mappings = {}

		dict_name = data["dtypes_loc"]#request.session['dtypes']
		indicator_value = mappings.pop("empty_indicator", None)
		country_value = mappings.pop("empty_country", None)
		indicator_category_value = mappings.pop("empty_indicator_cat", None)
		unit_of_measure_value = mappings.pop("empty_unit_of_measure", None)
		relationship_dict = mappings.pop("relationship", None)
		left_over_dict = mappings.pop("left_over", None)

		print('Here in this method')
		print(file_id)
		print(dict_name)

		with open(dict_name, 'rb') as f:
		    dtypes_dict = pickle.load(f)
		#check if exists
		if relationship_dict:
		#clean values of ~
		    for i in relationship_dict:
		        value = relationship_dict.pop(i)
		        key = i.replace("~", " ")
		        relationship_dict[key] = value

		    for i in left_over_dict:
		        value = left_over_dict.pop(i)
		        key = i.replace("~", " ")
		        left_over_dict[key] = value

		for key in mappings:
		        #return HttpResponse(key)
		    if mappings[key]:#this is included incase no mapping is given
		        #if not mappings[key][0] in df_data.columns:
		        #if mappings[key][0].replace("~", " ") in df_data.columns:
		        if len(mappings[key]) > 1:#greated than one for subgroups change for indicatpor scenario
		            if key == "indicator_category_id":
		                #ignore relationship
		                df_data["indicator_category_id"] = ""
		                tmp_mappings = ['indicator_category_id']
		                count = 0
		                for value in mappings[key]:
		                    mappings[key][count] = mappings[key][count].replace("~", " ")
		                    value = value.replace("~", " ")

		                    #loop through data combine with heading name and itself   
		                    if not value == 'indicator_category_id':
		                        if not relationship_dict:#no relationshup defined
		                                df_data["indicator_category_id"] = df_data["indicator_category_id"] + "|" + value + ":" + df_data[value].map(str)
		                        else:
		                            if not (value in relationship_dict):
		                                df_data["indicator_category_id"] = df_data["indicator_category_id"] + "|" + value + ":" + df_data[value].map(str)
		                            else:
		                                tmp_mappings.append(value)     
		                    count += 1
		                mappings[key] = tmp_mappings#IF RELATIONSHOip add here????
		                dtypes_dict[mappings['indicator_category_id'][0]] = [('str','str')]
		                #df_data['indicator_category_id'] =  tmp_col
		        else:
		            mappings[key][0] = mappings[key][0].replace("~", " ")

		if indicator_value:
		    mappings['indicator_id'] = ['indicator_id']
		    df_data['indicator_id'] = indicator_value
		    dtypes_dict[mappings['indicator_id'][0]] = [('str', 'str')]
		    #add indicator value as column 

		if country_value:
		    mappings['country_id'] = ['country_id']
		    df_data['country_id'] = country_value
		    dtypes_dict[mappings['country_id'][0]] = [('iso2', 'iso2')]

		if indicator_category_value:
		    mappings['indicator_category_id'] = ['indicator_category_id']
		    df_data['indicator_category_id'] = indicator_category_value
		    dtypes_dict[mappings['indicator_category_id'][0]] = [('str', 'str')]

		if unit_of_measure_value:
		    if len(unit_of_measure_value.keys()) < 2 :#chect each entry emoty unit_of measure a dict
		        mappings['unit_of_measure'] = ['unit_of_measure']
		        df_data['unit_of_measure'] = unit_of_measure_value[unit_of_measure_value.keys()[0]]
		        dtypes_dict[mappings['unit_of_measure'][0]] = [('str', 'str')]
		    else:
		        mappings['unit_of_measure'] = ['unit_of_measure']
		        dtypes_dict[mappings['unit_of_measure'][0]] = [('str', 'str')]

		if relationship_dict:
		    #check if unit of measure exists
		    df_data = convert_df(mappings, relationship_dict, left_over_dict, df_data, dtypes_dict, unit_of_measure_value)

		#remove replace
		#Validation
		for key in mappings:
		        #return HttpResponse(key)
		    if mappings[key]:#this is included incase no mapping is given
		        if key in mappings[key]:
		            mappings[key] = [key]
		        if not mappings[key][0] in df_data.columns:
		            mappings[key][0] = mappings[key][0].replace("~", " ")
		    #if (col.replace("~") in relationship_dict):
		    #    relationship_dict[col] = relationship_dict[col].replace("~", " ")

		    #for each line in df data
		#column_check = df_data.columns# 

		#Validation
		for key in mappings:
		        #return HttpResponse(key)
		        if mappings[key]:#this is included incase no mapping is given

		            #if not mappings[key][0] in df_data.columns:
		                #mappings[key][0] = mappings[key][0].replace("~", " ")
		            
		            correction_mappings[mappings[key][0]] = []
		            check = df_data[mappings[key][0]]
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
		    #for heading in request.session['missing_list']: #why not just pass missing list instead of missing
		    #    missing.append(heading.replace(" ", "~"))#check this
		    context = {"error_messages" : error_message, "success" : 0}
		    #return render(request, 'manual_mapping/manual_mapping.html', context)
		    #return HttpResponse(error_message)
		    return Response(context)
		df_data = correct_data(df_data, correction_mappings)

		#handle bad data
		null_values = df_data[mappings['indicator_category_id'][0]].isnull()
		df_data[mappings['indicator_category_id'][0]][null_values] = "Default"

		#df_data = df_data[1:len(df_data)]
		order = {}
		index_order = {}
		bulk_list = []

		#cycle through dataset and save each line
		order["file_source_id"] = file_id;#request.session['files'][0] 
		instance = FileSource(file_name = order['file_source_id'])
		instance.save()
		file_id = instance.id

		order['file_source_id'] = instance 
		order["date_created"] = datetime.datetime.now()
		instance = Time(date_type = "YYYY")
		instance.save()
		order['date_format_id'] = instance  

		datapoint_headings = []
		for key in mappings:
		    #if (not key == "file_name") or (not key == "indicator_category"):
		    if mappings[key]:
		        if mappings[key][0] in df_data.columns:#don't need this
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
		            instance = IndicatorSource.objects.filter(id = unique_list[index_order['source_id']][i].decode(errors='ignore'), indicator = ind_dict[unique_list[index_order['indicator_id']][i]]).first() 
		            if not instance:
		                instance = IndicatorSource(id = unique_list[index_order['source_id']][i].decode(errors='ignore'), indicator = ind_dict[unique_list[index_order['indicator_id']][i]])
		                instance.save()
		            ind_source_dict[unique_list[index_order['indicator_id']][i] + unique_list[index_order['source_id']][i]] = instance
		            
		        else:#indicator_sub
		            instance = Country.objects.filter(code = unique_list[i])
		            if instance.count() > 0:
		                #instance.save()
		                ind_country_dict[unique_list[i]] = instance[0]
		            else:#not in data base
		                instance = None#Country(code = unique_list[i])
		                #check = unique_list[i]
		                #try:
		                #    instance.save()
		                #    ind_country_dict[unique_list[i]] = instance
		                #except Exception as e:
		                    #instance = None
		                ind_country_dict[unique_list[i]] = instance
		    count += 1   
		count = 0


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
		#os.remove(dict_name)#remove tmp file with datatypes
		#Transgender people: HIV prevalence, 
		 #convert_to_JSON("Transgender people: HIV prevalence", "Transgender people: Population size estimate")#allow user to choose these

		#return HttpResponseRedirect('tags/%d'%file_id)
		#return nothing
		context = {"success" : 1}
		#return render(request, 'manual_mapping/manual_mapping.html', context)
		#return HttpResponse(error_message)
		return context
	else :
		context = {"error_messages" : "No data in dictionary sent", "success" : 0}
		return context