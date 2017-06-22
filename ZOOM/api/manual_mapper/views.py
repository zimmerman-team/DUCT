from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import django_rq

from manual_mapping.manual_mapper import manual_mapper
from lib.common import get_headings_data_model, get_file_data, get_dtype_data
from task_queue.tasks import manual_mapping_job
from file_upload.models import File


@api_view(['POST'])
def get_data(request):
    file_id = request.data['file_id']
    df_data = get_file_data(file_id)
    _, dtypes_dict = get_dtype_data(file_id)
    zip_list, summary_results, summary_indexes, remaining_mapping = get_headings_data_model(df_data, dtypes_dict)
    context = {
        'success': 1, 
        "found_list": zip_list, 
        "summary":zip(summary_indexes, summary_results),
        "missing_list" : remaining_mapping
    }

    return Response(context)


@api_view(['GET', 'POST'])
def ManualMapping(request):
    print request
    if request.method == 'POST':
        context = manual_mapper(request.data)
        return Response(context)
    else:
        return Response("No file selected");



class ManualMappingJob(APIView):
    """Manual Mapping Job"""

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (PublisherPermissions, )
    
    def post(self, request):

        from manual_mapping.manual_mapper import manual_mapper
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

