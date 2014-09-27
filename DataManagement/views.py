from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from  SmoWeb.settings import MEDIA_ROOT
import json
#from DataManagement.forms import ImportCSV_Form
import os.path
from utils import handle_uploaded_file, TemporaryKeyValueCollection, CSV2HDFImporter

# Create your views here.

CSVImporterObjects = TemporaryKeyValueCollection()

def importCSV(request):	
	if request.method == "POST":
		# process request data
		numRowsInPreview = int(request.POST.get('numRowsInPreview', 10))
		uploadedFile = request.FILES.get('file', '')		
		csvFile = handle_uploaded_file(uploadedFile, 
							 os.path.join(MEDIA_ROOT, 'DataManagement', 'csv'))
		# create the importer & create preview
		importer = CSV2HDFImporter(csvFile.name)
		importerId = CSVImporterObjects.push(importer)
		(numRows, numColumns, tableValues) = importer.createPreview(numRowsInPreview)

		response_data = {
			'numRows' : numRows,
			'numColumns' : numColumns,
			'tableValues' : tableValues,
			'importerId' : importerId
		}
		return JsonResponse(response_data)
	else:	
		return render_to_response('DataManagement/CSVpreview.html', 
								  context_instance=RequestContext(request))

def CSVtoHDF(request):
	if request.method == "POST":
		postData = json.loads(request.body)
		print postData
		columnProps = postData['columnProps']
		firstDataRow = int(postData['firstDataRow'])
		importerId = postData['importerId']
		importer = CSVImporterObjects.get(importerId)
		importer.import2Hdf(groupPath = "/", 
				datasetName = importer.csvFileName, 
				columnProps = columnProps, 
				firstDataRow = firstDataRow, 
				forceOverride = True)
		
	return HttpResponseRedirect(reverse('home'))
	