from django.http import HttpResponse
from django.shortcuts import render
from django.core.cache import cache
#from zoom_demo.lib.tools import check_column_type
import numpy as np

def index(request):
    #return HTTPResponse("Anseo anois")
    if request.method == 'POST':
        #context = {"files" : request.session['files'], "missing_headings" : request.session['missing_list'], "remaining_headings" : request.session['remaining_headings']}
        check = "Nothing"
        if 'dict' in request.POST:
            check = request.POST['dict']
        #check = request.POST["check"]
        #c = request.POST.get('mapping_dict')
        return HttpResponse(check) #render(request, 'manual_mapping/manual_mapping.html', context)    
    else:
        cache.clear() # check if necessary for ctrf token?   
        context = {}
        #request.session['found_mapping'] = zip_list
        #request.session['missing_list'] = missing_mapping
        #request.session['files'] = files
        context = {"files" : request.session['files'], "missing_headings" : request.session['missing_list'], "remaining_headings" : request.session['remaining_headings']}
        return render(request, 'manual_mapping/manual_mapping.html', context)