from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from  SmoWeb.settings import MEDIA_ROOT
import json
import os.path
from smo.util.django_utils import handle_uploaded_file, TemporaryObjectsHash
from smo.data.hdf import CSV2HDFImporter, HDFInterface

# Create your views here.

CSVImporterObjects = TemporaryObjectsHash()

def testView(request):
	if request.method == "POST":
		postData = json.loads(request.body)
		executeMethod = postData["executeMethod"]
		if (executeMethod == "getHdfFileContent"):
			filePath = "/data/Workspace/Django/SmoWeb/django-example/SmoWeb/media/DataManagement/csv/hdf/Rectangle_QuadrilateralMesh.hdf"
			hdfIface = HDFInterface(filePath)
			fileContent = [hdfIface.getFileContent()]
			return JsonResponse({'fileContent' : fileContent})

	else:
		return render_to_response('DataManagement/TestView.html', 
								  context_instance=RequestContext(request))

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
		return render_to_response('DataManagement/ImportCSV.html', 
								  context_instance=RequestContext(request))

def CSVtoHDF(request):
	if request.method == "POST":
		postData = json.loads(request.body)
		print postData
		columnProps = postData['columnProps']
		firstDataRow = int(postData['firstDataRow'])
		importerId = postData['importerId']
		importer = CSVImporterObjects.get(importerId)
		hdfFilePath = os.path.join(MEDIA_ROOT, 'DataManagement', 'csv', 'hdf', 'myData.hdf')
		importer.import2Hdf(filePath = hdfFilePath,
				groupPath = "/", 
				datasetName = importer.csvFileName, 
				columnProps = columnProps, 
				firstDataRow = firstDataRow, 
				forceOverride = True)
		CSVImporterObjects.pop(importerId)
		
	return HttpResponseRedirect(reverse('home'))
	