'''
Created on Sep 28, 2014

'''
import os
import csv
import h5py
import numpy as np
import json

class HDFInterface(object):
	def __init__(self, filePath):
		self.filePath = filePath
		self.fileName = os.path.basename(filePath)
		
	def getGroupContent(self, baseGroup, level = 0):
		if (level == 0):
			hdfFile = h5py.File(self.filePath)
			baseGroup = hdfFile[baseGroup]
		resultDict = []
		for name, item in baseGroup.iteritems():
			if (isinstance(item, h5py.Dataset)):
				resultDict.append({'type' : 'dataset', 'id' : hash(name), 'path' : item.name, 'name' : name, 'children' : []})
			elif (isinstance(item, h5py.Group)):
				children = self.getGroupContent(item, level + 1) 
				resultDict.append({'type' : 'group', 'id' : hash(name), 'path' : item.name, 'name' : name, 'children' : children, 'level' : level})
		if (level == 0):
			hdfFile.close()
		return resultDict
	
	def getFileContent(self, fileAsRoot = True):
		fileContent = self.getGroupContent('/')
		if (fileAsRoot):
			fileContent = {'type' : 'hdf_file', 'id' : hash(self.filePath), 'path' : self.filePath, 'name' : self.fileName, 'children' : fileContent}
		return fileContent

	@staticmethod
	def test():
		print ('test begin')
		filePath = "/data/Workspace/Django/SmoWeb/django-example/SmoWeb/media/DataManagement/csv/hdf/Rectangle_QuadrilateralMesh.hdf"
		a = HDFInterface(filePath)
		b = a.getFileContent()
		print (json.dumps(b, sort_keys=False, indent=4, separators=(',', ': ')))
		print ('test done')
	
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
	
	def import2Hdf(self, filePath, groupPath, datasetName, columnProps, 
				firstDataRow, forceOverride):
		hdfFile = h5py.File(filePath)

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
		
if __name__ == '__main__':
	HDFInterface.test() 