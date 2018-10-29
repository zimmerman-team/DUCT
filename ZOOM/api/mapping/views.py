from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import django_rq

from mapping.mapper import begin_mapping
from lib.common import get_headings_data_model, get_file_data, get_dtype_data
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


class MappingJob(APIView):
    """Mapping Job"""

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (PublisherPermissions, )
    
    def post(self, request):
        context = {}
        logger = logging.getLogger("django")
        logger.info("Entering Mapping Job")
        try:
            context = begin_mapping(request.data)
            logger.info("Successful mapping")
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception("--Error in mapping process")
            context['error'] = "Error occured when attempting to map file"
            context['success'] = 0
            raise #temp
        return Response(context)


class MappingJobResult(APIView):
    """ Mapping Job Results"""

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

