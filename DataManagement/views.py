from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from  SmoWeb.settings import MEDIA_ROOT, hdfFileFolder
import json
import os.path
from smo.util.django_utils import handle_uploaded_file, TemporaryObjectsHash
from smo.data.hdf import CSV2HDFImporter, HDFInterface

# Create your views here.

CSVImporterObjects = TemporaryObjectsHash()

def hdfInterfaceView(request):
	if request.method == "POST":
		postData = json.loads(request.body)
		action = postData["action"]
		input = postData["input"]
		currentNode = postData["currentNode"]
# 		print postData
		
# 		action = postData["action"]
	#hdfFileId = postData["hdfFileId"]
		hdfFileName = "myData.hdf" # !!! Actually here the name corresponding to the id should be used
		hdfFilePath = os.path.join(hdfFileFolder, hdfFileName)
		if (action == "getHdfFileContent"):
			hdfIface = HDFInterface(hdfFilePath)
			fileContent = [hdfIface.getFileContent()]
			return JsonResponse({'fileContent' : fileContent})
		elif (action == "copy"):
			hdfIface = HDFInterface(hdfFilePath)
			itemPath = currentNode["path"]
			pasteRoot = input
			name = currentNode["name"]
			print itemPath, pasteRoot, name			
			hdfIface.copyItem(itemPath, pasteRoot, name)
			
		elif (action == "createGroup"):			
			hdfIface = HDFInterface(hdfFilePath)
			hdfIface.createGroup(currentNode["path"], input)
			
		elif (action == "rename"):
			hdfIface = HDFInterface(hdfFilePath)
			itemPath = currentNode["path"]
			newName = input
			pasteRoot = os.path.dirname(itemPath)
# 			name = currentNode["name"]
# 			print itemPath, pasteRoot
			hdfIface.moveItem(itemPath, pasteRoot, newName)
		elif (action == "move"):
			hdfIface = HDFInterface(hdfFilePath)
			itemPath = currentNode["path"]
			pasteRoot = input
			name = currentNode["name"]
			print itemPath, pasteRoot
			hdfIface.moveItem(itemPath, pasteRoot, name)
		
		elif (action == "delete"):
			hdfIface = HDFInterface(hdfFilePath)
			hdfIface.deleteItem(currentNode["path"])
		return HttpResponseRedirect(reverse('home'))
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
		hdfFilePath = os.path.join(MEDIA_ROOT, 'DataManagement', 'hdf', 'myData.hdf')
		importer.import2Hdf(filePath = hdfFilePath,
				groupPath = "/", 
				datasetName = importer.csvFileName, 
				columnProps = columnProps, 
				firstDataRow = firstDataRow, 
				forceOverride = True)
		CSVImporterObjects.pop(importerId)
		
	return HttpResponseRedirect(reverse('home'))
	