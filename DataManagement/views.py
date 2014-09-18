from django.shortcuts import render_to_response, RequestContext
from DataManagement.forms import ImportCSV_Form
from  SmoWeb.settings import MEDIA_ROOT
import os.path
from utils import handle_uploaded_file

# Create your views here.

def importCSV(request):
    if request.method == "POST":
        form = ImportCSV_Form(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['csvFile'], 
                                 os.path.join(MEDIA_ROOT, 'DataManagement', 'csv'))
            errMessage = ""
        else:
            errMessage = "Invalid form data"
        
        #print request.FILES
        #print form.cleaned_data['csvFile']
        #print form.cleaned_data['hdfPath']
                                
    else:
        form = ImportCSV_Form()
        errMessage = ""
    return render_to_response('CSVform.html', locals(), context_instance=RequestContext(request))