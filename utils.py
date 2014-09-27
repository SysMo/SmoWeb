'''
Created on Sep 17, 2014

@author: ivaylo
'''
import csv
import numpy as np
import glob
import os
from django.db.utils import OperationalError

def handle_uploaded_file(f, media_path):
	destination = open(os.path.join(media_path, f.name), 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()
	return destination


import uuid
class TemporaryKeyValueCollection:
	def __init__(self, klass = object):
		self.klass = klass
		self.collection = {}
		
	def push(self, instance, key = None):
		if (not isinstance(instance, self.klass)):
			raise TypeError('Attempt to add instance of type ' + type(instance)
					+ ' to collection of type ' + self.klass)
		if (key == None):
			key = uuid.uuid4().hex
		self.collection[key] = instance
		return key
	
	def get(self, key):
		return self.collection.get(key)
	
	def pop(self, key):
		return self.collection.pop(key)

import h5py
import numpy as np
from  SmoWeb.settings import MEDIA_ROOT
class CSV2HDFImporter(object):
	typeDict = {'float' : 'f', 'integer' : 'i', 'string' : 'S100'}
	typeCastFunc = {'float' : float, 'integer' : int, 'string' : str}
	def __init__(self, filePath, firstDataRowIndex = 1):
		self.filePath = filePath
		self.csvFileName = os.path.basename(filePath)
		self.firstDataRowIndex = firstDataRowIndex
		
	def createPreview(self, numRowsInPreview):
		f = open(self.filePath, 'r')
		reader = csv.reader(f)
		previewValues = []
		self.numRows = 0
		numColumns = 1
		for row in reader:
			self.numRows += 1
			if (len(row[:]) > numColumns):
					numColumns = len(row[:])
			if (self.numRows <= numRowsInPreview):				
				previewValues.append(row)
		f.close()
		return (self.numRows, numColumns, previewValues)
	
	def import2Hdf(self, groupPath, datasetName, columnProps, 
				firstDataRow, forceOverride):
		hdfFile = h5py.File(os.path.join(MEDIA_ROOT, 'DataManagement', 'csv', 'hdf', 'myData.hdf'))

		group = hdfFile[groupPath]
		if (datasetName in group):
			if (forceOverride):
				del group[datasetName]
			else:
				raise IOError('Dataset with name ' + datasetName + 
							' already exists in ' + groupPath + 
							"\nEither change the name or select 'Force override'")
		# Define the size and type of the dataset
		datasetNumRows = self.numRows - firstDataRow + 1
		datasetTypeList = []
		for colProp in columnProps:
			if (colProp['use']):
				datasetTypeList.append((str(colProp['name']), self.typeDict[colProp['dataType']]))
		datasetType = np.dtype(datasetTypeList)

		dataset = group.create_dataset(datasetName, 
					shape = (datasetNumRows,), dtype = datasetType)
		f = open(self.filePath)
		reader = csv.reader(f)
		rowIndex = 0
		for row in reader:
			rowIndex += 1
			if (rowIndex < firstDataRow):
				continue
			columnIndex = 0
			datasetRowValues = []
			for data in row:
				colProp = columnProps[columnIndex]
				if (colProp['use']):
					datasetRowValues.append(self.typeCastFunc[colProp['dataType']](data))
				columnIndex +=1
			dataset[rowIndex - firstDataRow] = tuple(datasetRowValues)
					
		f.close()
		hdfFile.close()

	@staticmethod
	def test(filePath):
		reader = CSV2HDFImporter(filePath)
		reader.initialRead()
