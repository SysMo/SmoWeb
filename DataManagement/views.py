from django.shortcuts import render_to_response, RequestContext
from DataManagement.forms import ImportCSV_Form
from  SmoWeb.settings import MEDIA_ROOT
import os.path
from utils import handle_uploaded_file, CSVReader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import json
import h5py
import numpy as np

# Create your views here.

def importCSV(request):	
	if request.method == "POST":
#		 print type(request.POST)
		rowsInDisplay = int(request.POST.get('rowsInDisplay', 10))
		uploadFile = request.FILES.get('file', '')
		csvFile = handle_uploaded_file(uploadFile, 
							 os.path.join(MEDIA_ROOT, 'DataManagement', 'csv'))

		readerInstance = CSVReader(csvFile.name)
		(numRows, numColumns, tableValues) = readerInstance.initialRead()
		if rowsInDisplay > len(tableValues):
			rowsInDisplay = len(tableValues)
		tableValues = tableValues[:rowsInDisplay]
		
#			 return HttpResponse(json.dumps(response_data), content_type="application/json")
#			 return HttpResponseRedirect(reverse('DataManagement:PreviewCSV'), 
#										 content=json.dumps(response_data), content_type="application/json")
		response_data = {}
		response_data['numRows'] = numRows
		response_data['numColumns'] = numColumns
		response_data['tableValues'] = tableValues
		response_data['filePath'] = csvFile.name
		return HttpResponse(json.dumps(response_data), content_type="application/json")					 
		
	return render_to_response('DataManagement/CSVpreview.html', 
							  context_instance=RequestContext(request))

def CSVtoHDF(request):
	if request.method == "POST":
		data = json.loads(request.body)
		print data
		hdfFile = h5py.File("/data/Workspace/Django/django-example/SmoWeb/media/DataManagement/csv/hdf/myData.hdf")
		csvNumRows = int(data['numRows'])
		firstDataRow = int(data['firstDataRow'])
		datasetNumRows = csvNumRows - firstDataRow + 1
		datasetNumColumns = 0;
		datasetTypeList = []
		typeDict = {'float' : 'f', 'integer' : 'i', 'string' : 'S100'}
		for useColumn, columnName, columnType in \
				zip(data['useColumn'], data['columnNames'], data['columnTypes']):
			if (useColumn):
				datasetNumColumns += 1
				datasetTypeList.append((str(columnName), typeDict[columnType]))
		datasetType = np.dtype(datasetTypeList)
		if ('ng_rules' in hdfFile.keys()):
			del hdfFile['ng_rules']
		hdfFile.create_dataset('ng_rules', (datasetNumRows,), datasetType)
		hdfFile.close()
		
#		columnNames : $scope.columnNames,
#		useColumn : $scope.useColumn,
#		columnTypes : $scope.columnTypes,
#		firstDataRow : $scope.firstDataRow,
#		 numRows : $scope.numRows,
#		filePath : $scope.filePath
	return HttpResponseRedirect(reverse('home'))
	