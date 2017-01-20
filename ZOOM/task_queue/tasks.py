# from iati_synchroniser.models import IatiXmlSource
# from iati.activity_aggregation_calculation import ActivityAggregationCalculation
from django_rq import job
import django_rq
import datetime
from rq import Queue, Connection, Worker
from rq.job import Job
from redis import Redis
from django.conf import settings
import time


redis_conn = Redis()

