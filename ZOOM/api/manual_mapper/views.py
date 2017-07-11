from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import django_rq

from manual_mapping.manual_mapper import manual_mapper
from lib.common import get_headings_data_model, get_file_data, get_dtype_data
from task_queue.tasks import manual_mapping_job
from file_upload.models import File
import time


@api_view(['POST'])
def get_data(request):
    file_id = request.data['file_id']
    
    df_data = get_file_data(file_id)
    # Future: make faster by only reading in headings or 1st row rather than entire data set
    zip_list, summary_results, summary_indexes, remaining_mapping = get_headings_data_model(df_data)
    #Future: add summary for hover over file heading name
    context = {
        'success': 1, 
        "found_list": zip_list, 
        "summary":zip(summary_indexes, summary_results),
        "missing_list" : remaining_mapping
    }

    return Response(context)


@api_view(['POST'])
def ManualMapping(request):
    if request.method == 'POST':
        print("Incoming Request")
        print(request)
        print("Entering Manual Mapping")
        print (time.strftime("%H:%M:%S"))
        context = manual_mapper(request.data)
        print("Finished")
        print(context)

        # Clear /indicator/aggregations caches
        cache.clear()
        # TODO - check if the above also deletes tasks from the task queue, if so, make separates caches in the settings - 2017-07-05
        
        return Response(context)
    else:
        return Response("No file selected");



class ManualMappingJob(APIView):
    """Manual Mapping Job"""

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (PublisherPermissions, )
    
    def post(self, request):

        from manual_mapping.manual_mapper import manual_mapper
        print("In Job")
        print("Incomming Request")
        print(request)
        print("Entering Manual Mapping")
        print (time.strftime("%H:%M:%S"))
        context = manual_mapper(request.data)
        return Response(context)


class ManualMappingJobResult(APIView):
    """Manual Mapping Job Results"""

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (PublisherPermissions, )
    
    def post(self, request):
        job_id = request.data["job_id"]
        job_id = job_id.split(':')[2]

        queue = django_rq.get_queue('mapper')
        job = queue.fetch_job(job_id)

        if job.is_finished:
            ret = {'status':'completed', 'result': job.return_value}

            try:
                file = File.objects.get(id=request.data["file_id"])
            except File.DoesNotExist:
                return Response({
                    'status': 'failed',
                })

            file.in_progress = False
            file.save()

        elif job.is_queued:
            ret = {'status':'in-queue'}
        elif job.is_started:
            ret = {'status':'waiting'}
        elif job.is_failed:
            ret = {'status': 'failed'}
            print(job.to_dict())


        return Response(ret)

