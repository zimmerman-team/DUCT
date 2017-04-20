import pandas as pd
import numpy as np
import json
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.conf import settings

from api.uploads.serializers import FileSerializer
from validate.models import File
from indicator.models import IndicatorDatapoint
from geodata.models import get_dictionaries
from lib.tools import  identify_col_dtype


class UploadsCreateList(ListCreateAPIView):

    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('file_name', 'file', 'created')

    fields = (
        'file_name',
        'file'
        )

    def perform_create(self, serializer):
        serializer.save(file=self.request.data.get('file'), file_name=self.request.data.get('file_name'))


class ErrorCorrectionView(APIView):

    def post(seld, request, *args, **kwargs):

        file_name = request.data.get('file_name').split("/")[-1]

        df_data = pd.read_csv(settings.MEDIA_ROOT + "/datasets/" + str(file_name))

        
        '''
        Create FileSource
        '''



        '''
        Validate View
        '''

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

  
        file_heading_list = df_data.columns
        #sample_amount = len(df_file[file_heading_list[0]]) # might be too big, might take too long
        template_heading_list = []

        #Get datapoint headings
        for field in IndicatorDatapoint._meta.fields:
            template_heading_list.append(field.name)#.get_attname_column())
        
        template_heading_list = template_heading_list[4:len(template_heading_list)]#skip first four headings as irrelevant to user input
        template_heading_list.append("unit_measure") #needed? 
        
        #count = 0# not sure if this is still needed, might need for matches
        dicts, _ = get_dictionaries()#get dicts for country
        #c = _
        #g = dicts
        for heading in file_heading_list:
            headings_file[heading] = count
            prob_list, error_count = identify_col_dtype(df_data[heading], heading, dicts)
            dtypes_dict[heading] = prob_list 
            
            error_lines.append(error_count)
            validation_results.append(df_data[heading].isnull().sum())
            dtypes_list.append(prob_list) 
            #count += 1

        count = 0 #count matching
        overall_count = len(template_heading_list)

        for key in template_heading_list:
          remaining_mapping.append(key)
        
        zip_list = zip(file_heading_list, dtypes_list, validation_results)#zip(found_mapping, mapping, data_types, validation_on_types)
        missing_mapping = list(headings_file.keys())
        

        context = {'mapped' : count, "no_mapped" : overall_count - count, "found_list": zip_list, "missing_list" : remaining_mapping}#reorganise messy

        print context


        '''
        Error Correct View
        '''

        line_numbers = []
        data_list = []
        found_error_ids = []
        error_ids = []

        column_headings = list(df_data.columns)

        # error_data = request.session['missing_dtypes_list']
        error_data = error_lines

        line_no = np.array([])
        pointer = []
        for i in range(len(column_headings)):
            data_types = np.array([j[0] for j in error_data[i]]) 
            indexes = np.where(data_types != dtypes_dict[column_headings[i]][0][0])
            line_no = np.append(line_no, indexes)
        error_line_no = np.unique(line_no)

        file_error = {}
        file_error['data'] = []
        # file_error['heading'] = ['id'] + column_headings
        file_error['heading'] = column_headings

        if len(error_line_no) <= 200: 

            for i in error_line_no:
                i = int(i)
                temp_list = []
                temp_error_ids = []
                for j in range(len(column_headings)):
                    if dtypes_dict[column_headings[j]][0][0] != error_data[j][i][0]:
                        #log line to highlight
                        found_error_ids.append((str(i+1)+"_"+column_headings[j], "found " + error_data[j][i][0] + " should be " + dtypes_dict[column_headings[j]][0][0]))
                        #found_error = True
                    temp_list.append(df_data.iloc[i, j])
                    temp_error_ids.append(str(i+1)+"_"+ column_headings[j])
                #if found_error:
                line_numbers.append(i + 1)
                data_list.append(zip(temp_list, temp_error_ids))

                item = {}
                # print column_headings
                item['id'] = i + 1
                for j in range(len(column_headings)):
                    if dtypes_dict[column_headings[j]][0][0] != error_data[j][i][0]:
                        found_error_ids.append((str(i+1)+"_"+column_headings[j], "found " + error_data[j][i][0] + " should be " + dtypes_dict[column_headings[j]][0][0]))
                    item[column_headings[j]] = df_data.iloc[i, j]
                    if str(item[column_headings[j]]) == "nan":
                        item[column_headings[j]] = "nan"
                file_error['data'].append(item)
            zip_list = zip(line_numbers, data_list)
            context= {"df_data" : zip_list, "column_headings":column_headings, "found_error_ids" : found_error_ids}
        else:
            error_count = len(error_line_no)
            list_of_errors = [] 
            context = {"error_count": len(error_line_no), "list of errors": list_of_errors}
        print file_error
        return Response(file_error, status=HTTP_200_OK)


