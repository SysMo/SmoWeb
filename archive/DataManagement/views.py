from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from  SmoWeb.settings import MEDIA_ROOT, HDF_FOLDER
import json
import os.path
from smo.web.util import handle_uploaded_file, TemporaryObjectsHash
from smo.data.hdf import CSV2HDFImporter, HDFInterface
from smo.web.view import ModularPageView
from smo.web.modules import HtmlModule

CSVImporterObjects = TemporaryObjectsHash()

def hdfInterfaceView(request):
	if request.method == "POST":
		postData = json.loads(request.body)
		action = postData["action"]
		hdfNode = postData["currentNode"]		
		hdfFileName = "myData.hdf" # !!! Actually here the name corresponding to the id should be used
		hdfFilePath = os.path.join(HDF_FOLDER, hdfFileName)
		hdfIface = HDFInterface(hdfFilePath)		
		if (action == "getHdfFileContent"):			
			fileContent = [hdfIface.getFileContent()]
			return JsonResponse({'fileContent' : fileContent})
		elif (action == "copy"):
			itemPath = hdfNode["path"]
			pasteRoot = postData["input"]
			name = hdfNode["name"]	
			hdfIface.copyItem(itemPath, pasteRoot, name)			
		elif (action == "createGroup"):			
			hdfIface.createGroup(hdfNode["path"], postData["input"])			
		elif (action == "rename"):
			itemPath = hdfNode["path"]
			newName = postData["input"]
			pasteRoot = os.path.dirname(itemPath)
			hdfIface.moveItem(itemPath, pasteRoot, newName)
		elif (action == "move"):
			itemPath = hdfNode["path"]
			pasteRoot = postData["input"]
			name = hdfNode["name"]
			hdfIface.moveItem(itemPath, pasteRoot, name)		
		elif (action == "delete"):
			hdfIface.deleteItem(hdfNode["path"])
		elif (action == "view"):
			datasetPath = hdfNode["path"]
			jsonContent = hdfIface.getDatasetContent(datasetPath)
			return HttpResponse(jsonContent, content_type="application/json")
		return HttpResponseRedirect(reverse('home'))
	else:
		return render_to_response('DataManagement/HdfInterface.html', 
								  context_instance=RequestContext(request))

class DataExplorer(HtmlModule):
	srcType = 'file'

class DataExplorerView(ModularPageView):
	label = 'Data Explorer'
	modules = [DataExplorer]

class ImportCsv(HtmlModule):
	srcType = 'file'

class ImportCsvView(ModularPageView):
	label = 'Import CSV'
	modules = [ImportCsv]
	
	def post(self, request):
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
			'importerId' : importerId,
			'csvFileName' : importer.csvFileName
		}
		return JsonResponse(response_data)
	
	
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
			'importerId' : importerId,
			'csvFileName' : importer.csvFileName
		}
		return JsonResponse(response_data)
	else:	
		return render_to_response('DataManagement/ImportCSV.html', 
								  context_instance=RequestContext(request))

def CSVtoHDF(request):
	if request.method == "POST":
		postData = json.loads(request.body)
		columnProps = postData['columnProps']
		firstDataRow = int(postData['firstDataRow'])
		importerId = postData['importerId']
		groupPath = postData['groupPath']
		datasetName = postData['datasetName']
				
		importer = CSVImporterObjects.get(importerId)		
		hdfFilePath = os.path.join(MEDIA_ROOT, 'DataManagement', 'hdf', 'myData.hdf')
				
		importer.import2Hdf(filePath = hdfFilePath,
				groupPath = groupPath, 
				datasetName = datasetName, 
				columnProps = columnProps, 
				firstDataRow = firstDataRow, 
				forceOverride = True)
		CSVImporterObjects.pop(importerId)