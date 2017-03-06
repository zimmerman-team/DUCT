from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'scatter_demo/index.html', context) #render(request, 'manual_mapping/manual_mapping.html', context) 


def data_selector(request):
    context = {}
    return render(request, 'selector/main.html', context)

def scatter_api(request):
    context = {}
    return render(request, 'scatter_api/index.html', context)


def create_tags(request):
	if request.method == 'POST':
		for i in range(0,len(request.POST)-1):
			print request.POST['tags[' + str(i) + '][tag]']

	return HttpResponse('')


def tags(request):
    context = {}
    print "Aha"
    print request.POST
    return render(request, 'tags/tags.html', context)