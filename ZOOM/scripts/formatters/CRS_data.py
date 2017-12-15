#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
from file_upload.models import File

WB = "World Bank"
CRS = "CRS"
file_dict = {
				WB:{}, 
				CRS:{tag:"CRS", source:"CRS", mapping:[], input_path:"CRS/input/", output_path:"CRS/output/", headings:[] }
			}
file_list = [WB, CRS]
character_sep = {WB: ",", CRS: "|"}

def main():
	global character_sep
	checked = false
	print("Enter one of the following: ", file_list)
	print("e for escape")
	while(checked):
		file_choice = raw_input("Enter data desired from above:")
		if(file_choice in file_list):
			checked = True
		elif(file_choice == "e"):
			sys.exit()

	convert_data(file_choice)
	start_mapping(file_choice)

def start_mapping(file_choice):
	global file _list

	file_list = os.listdir(file_dict[file_choice].input_path)
	counter = 0

	for file_name in file_list:
		print("-------------------------")
		print("Mapping File", file_name)
		File(title=)
		title = models.CharField(max_length=100)
	    description = models.TextField(null=False, blank=False)
	    tags = models.ManyToManyField(FileTag)
	    data_source = models.ForeignKey(FileSource, null=True, on_delete=models.SET_NULL)
	    in_progress = models.BooleanField(default=False)
	    source_url = models.URLField(null=True, max_length=2000)
	    file = models.FileField(upload_to=upload_to)
	    file_name = models.CharField(max_length = 200, default="default")
	    created = models.DateTimeField(auto_now_add=True, null=True)
	    modified = models.DateTimeField(auto_now=True, null=True)
	    rendered = models.BooleanField(default=False)
	    status = models.IntegerField(default=1)
	    authorised = models.BooleanField(default=False, db_index=True)
	    mapping_used = models.CharField(max_length=100000, null=True, blank=True)

"""Year: Date Value
DonorName:	Category	
CRSid category UID
RecipientName	Country	
RegionName	See note--> 	since your framework doesn’t allow for region, and it's not really a separate category to pivot on, I think we can ignore, though it would be helpful to be able to roll up figures into regional sums
IncomegroupName	See note--> 	same thing here - not really a category, no additional information added to the country, but useful if we can allow users to select totals by income group
FlowName	Indicator	see FlowName tab (this one isn't included in the official codelist) - 1/3 of the indicator
Finance_t	Category	see finance_types codelist
Aid_t	Category	see aid_types codelist
usd_commitment	Indicator/Value	These 6 fields (of which we'll only use 4) actually represent the other 2/3s of the indicator and then the values themselves: Amount Type indicator (current or constant*); FlowType indicator (Commitment/Disbursement/Received, but lets ignore Received) (*NOTE: current prices are always from the year they were disbursed, constant prices are always deflated to the previous year in which the DATA was compiled, so if this is 2016 data, constant prices are in 2015 figures)
usd_disbursement	Indicator/Value	
usd_commitment_defl	Indicator/Value	
usd_disbursement_defl	Indicator/Value	
CurrencyCode	See note--> 	Based on donor country - looks like either 302 (USD) or 918 (Euros) - so I guess this could be a Category to allow for conversions?
PurposeName	Category	see codelist (DAC 5)
SectorName	Category	see codelist (DAC 3)"""



"""
Created on Mon Nov 20 09:42:29 2017
@author: marco
This script format crs data: 
    The original file uses "|" instead of ","
"""
def convert_data(file_choice):
	global character_sep, file_dict
	file_list = os.listdir(file_dict[file_choice].input_path)
	counter = 0
	#get files in folder
	print("Begining Conversion")
	
	for file_name in file_list:
	    data = pd.read_csv(file_dict[file_choice].input_path + file_name, sep=character_sep[file_choice])
    	##check column width and size an split accoringly
    	data.to_csv(file_dict[file_choice].output_path + file_name[:-4]+".csv", sep=',', index = False)
    	sys.stdout.write("\r%d%%" % ((counter/len(file_list)) * 100) )

	sys.stdout.flush()
	#print("All files converted")

def mapping(mapping_dict, file):
	print("Begining Mapping ", file)

	print("Finished Mapping ", file)

if __name__ == "__main__":
    main()