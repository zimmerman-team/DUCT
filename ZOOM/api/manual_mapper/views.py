from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import django_rq

from manual_mapping.manual_mapper import manual_mapper
from task_queue.tasks import manual_mapping_job
from file_upload.models import File


@api_view(['GET', 'POST'])
def ManualMapping(request):
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
        try:
            file = File.objects.get(id=request.data["file_id"])
        except File.DoesNotExist:
            return Response({
                'status': 'File not found',
            })

        if file.in_progress:
            return Response({
                'status': 'failed',
            })


        file.in_progress = True
        file.save()

        queue = django_rq.get_queue('mapper')
        job = queue.enqueue(manual_mapping_job, request.data)

        return Response({
            'status': 'processing',
            'job': job.key,
        })


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

