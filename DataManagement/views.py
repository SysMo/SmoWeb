from django.shortcuts import render_to_response, RequestContext
from DataManagement.forms import ImportCSV_Form
from  SmoWeb.settings import MEDIA_ROOT
import os.path

# Create your views here.

def handle_uploaded_file(f):
    destination = open(os.path.join(MEDIA_ROOT,'csv/temp.csv'), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def importCSV(request):
    if request.method == "POST":
        form = ImportCSV_Form(request.POST, request.FILES)
        if form.is_valid():
            print request.FILES['csvFile']
            handle_uploaded_file(request.FILES['csvFile'])
        else:
            raise ValueError("Invalid form data")
        #print request.FILES
        #print form.cleaned_data['csvFile']
        #print form.cleaned_data['hdfPath']
                                
    form = ImportCSV_Form()
    return render_to_response('CSVform.html', locals(), context_instance=RequestContext(request))