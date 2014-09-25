from django.shortcuts import render_to_response, RequestContext
from DataManagement.forms import ImportCSV_Form
from  SmoWeb.settings import MEDIA_ROOT
import os.path
from utils import handle_uploaded_file, CSVReader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import json

# Create your views here.

def importCSV(request):    
    if request.method == "POST":
        form = ImportCSV_Form(request.POST, request.FILES)
        if form.is_valid():
            errMessage = ""
            file = handle_uploaded_file(form.cleaned_data['csvFile'], 
                                 os.path.join(MEDIA_ROOT, 'DataManagement', 'csv'))

            print file
            readerInstance = CSVReader(file.name)
            
            rowsInDisplay = form.cleaned_data['rowsInDisplay']     
            numRows = readerInstance.initialRead()['numRows']
            numColumns = readerInstance.initialRead()['numColumns']
            tableValues = readerInstance.initialRead()['tableValues']
            if rowsInDisplay > len(tableValues):
                rowsInDisplay = len(tableValues)
            else:
                tableValues = tableValues[:rowsInDisplay]
            
        
#             return HttpResponse(json.dumps(response_data), content_type="application/json")
#             return HttpResponseRedirect(reverse('DataManagement:PreviewCSV'), 
#                                         content=json.dumps(response_data), content_type="application/json")
            print numRows
            print numColumns
            print tableValues
            print rowsInDisplay
            return render_to_response('DataManagement/CSVpreview.html', 
                            locals(), context_instance=RequestContext(request))
        else:
            errMessage = "Invalid form data"                              
    else:              
        errMessage = ""
        form = ImportCSV_Form()        
        rowsInDisplay = 10 
    return render_to_response('DataManagement/CSVform.html', 
                              locals(), context_instance=RequestContext(request))

def CSVtoHDF(request):
    if request.method == "POST":
        print "POST Success!!!!"
        data = json.loads(request.body)
        print data
    else:
        print "Success!!!!"
    return HttpResponseRedirect(reverse('home'))
    