from django.shortcuts import render_to_response, RequestContext
from DataManagement.forms import ImportCSV_Form
from  SmoWeb.settings import MEDIA_ROOT
import os.path
from utils import handle_uploaded_file, CSVReader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import json

# Create your views here.

def importCSV(request):    
    if request.method == "POST":
#         print type(request.POST)
        rowsInDisplay = int(request.POST.get('rowsInDisplay', 10))
        uploadFile = request.FILES.get('file', '')
        csvFile = handle_uploaded_file(uploadFile, 
                             os.path.join(MEDIA_ROOT, 'DataManagement', 'csv'))

        readerInstance = CSVReader(csvFile.name) 
        numRows = readerInstance.initialRead()['numRows']
        numColumns = readerInstance.initialRead()['numColumns']
        tableValues = readerInstance.initialRead()['tableValues']
        print len(tableValues)
        print rowsInDisplay
        print (rowsInDisplay > len(tableValues))
        if rowsInDisplay > len(tableValues):
            rowsInDisplay = len(tableValues)
        
        print rowsInDisplay
        tableValues = tableValues[:rowsInDisplay]
#         print tableValues
#         print tableValues[0:5]
           
        
        
#             return HttpResponse(json.dumps(response_data), content_type="application/json")
#             return HttpResponseRedirect(reverse('DataManagement:PreviewCSV'), 
#                                         content=json.dumps(response_data), content_type="application/json")
        response_data = {}
        response_data['numRows'] = numRows
        response_data['numColumns'] = numColumns
        response_data['tableValues'] = tableValues
#         print tableValues;
#         response_data['rowsInDisplay'] = rowsInDisplay
        return HttpResponse(json.dumps(response_data), content_type="application/json")                     
        
    return render_to_response('DataManagement/CSVpreview.html', 
                              context_instance=RequestContext(request))

def CSVtoHDF(request):
    if request.method == "POST":
        print "POST Success!!!!"
        data = json.loads(request.body)
        print data
    else:
        print "Success!!!!"
    return HttpResponseRedirect(reverse('home'))
    