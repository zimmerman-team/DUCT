from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from django.db import connections
from django.db import OperationalError


@api_view(('GET',))
def welcome(request, format=None):
    """
    ## REST API

    The REST API provides programmatic access to read (and soon also write) indicator data.
    The REST API responses are available in JSON.

    ## Available endpoints

    * Indicators: [`/api/indicators`](/api/indicators)

    """
    return Response({
        'endpoints': {
            'indicators': reverse(
                'indicators:indicator-list',
                request=request,
                format=format),
            'scatter': reverse(
                'scatter:scatter-list',
                request=request,
                format=format),
            'uploads': reverse(
                'uploads:files-list',
                request=request,
                format=format),
        }
    })


@api_view(('GET',))
def health_check(request, format=None):
    """
    Performs an API health check
    """
    okay = True

    conn = connections['default']
    try:
        c = conn.cursor()
    except OperationalError:
        okay = False

    if okay is False:
        return Response(status=500)

    return Response(status=200)