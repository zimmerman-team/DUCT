from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import django_rq

from manual_mapping.manual_mapper import manual_mapper
from lib.common import get_headings_data_model, get_file_data, get_dtype_data
from task_queue.tasks import manual_mapping_job
from metadata.models import File
import time
import logging
import datetime

@api_view(['POST'])
def get_data(request):
    context = {'success':0}
    try:
        id = request.data['id']
        
        df_data = get_file_data(id)
        # Future: make faster by only reading in headings or 1st row rather than entire data set
        zip_list, summary_results, summary_indexes, remaining_mapping = get_headings_data_model(df_data)
        #Future: add summary for hover over file heading name
        context = {
            'success': 1, 
            "found_list": zip_list, 
            "summary":zip(summary_indexes, summary_results),
            "missing_list" : remaining_mapping
        }
    except Exception as e:
        logger = logging.getLogger("django")
        logger.exception("--Error in get data occurred")
        context['error'] = "Problem retrieving column name from file"
        context['success'] = 0
        raise
    return Response(context)


@api_view(['POST'])
def ManualMapping(request):
    context = {}
    if request.method == 'POST':
        logger = logging.getLogger("django")
        try:
            logger.info("Entering Manual Mapping")
            context = manual_mapper(request.data)
            logger.info("Successful mapping")
        except Exception as e:
            logger.exception("--Error in manual mapping process")
            context['error'] = "Error occured when attempting to map file"
            context['success'] = 0
            raise #temp
        # Clear /indicator/aggregations caches
        #cache.clear()
        print("Should respond")
        # TODO - check if the above also deletes tasks from the task queue, if so, make separates caches in the settings - 2017-07-05
        print("reponse, ", Response())
        return Response()
        #return Response(context)
    else:
        return Response("No file selected");



class ManualMappingJob(APIView):
    """Manual Mapping Job"""

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (PublisherPermissions, )
    
    def post(self, request):
        from manual_mapping.manual_mapper import manual_mapper
        context = {}
        logger = logging.getLogger("django")
        logger.info("Entering Manual Mapping Job")
        try:
            context = manual_mapper(request.data)
            logger.info("Successful mapping")
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception("--Error in manual mapping process")
            context['error'] = "Error occured when attempting to map file"
            context['success'] = 0
            raise #temp
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
                file = File.objects.get(id=request.data["id"])
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

