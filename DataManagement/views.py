from django.shortcuts import render_to_response, RequestContext
from DataManagement.forms import ImportCSV_Form
from  SmoWeb.settings import MEDIA_ROOT
import os.path
from utils import handle_uploaded_file
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.

def importCSV(request):
    if request.method == "POST":
        form = ImportCSV_Form(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['csvFile'], 
                                 os.path.join(MEDIA_ROOT, 'DataManagement', 'csv'))
            rowsInDisplay = form.cleaned_data['rowsInDisplay']
            errMessage = ""           
            return render_to_response('DataManagement/CSVpreview.html', 
                              locals(), context_instance=RequestContext(request))
        else:
            errMessage = "Invalid form data"                              
    else:
        form = ImportCSV_Form()
        errMessage = ""
        rowsInDisplay = 10 
    return render_to_response('DataManagement/CSVform.html', 
                              locals(), context_instance=RequestContext(request))
