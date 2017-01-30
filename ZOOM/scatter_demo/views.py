from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'scatter_demo/index.html', context) #render(request, 'manual_mapping/manual_mapping.html', context) 


def data_selector(request):
    context = {}
    return render(request, 'selector/main.html', context)