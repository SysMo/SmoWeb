'''
Created on Sep 25, 2014

@author: ivaylo
'''
import csv
import numpy as np
import glob
import os

class Table2DReader:
    def __init__(self, filePath):
        self.filePath = filePath
    
    def read(self):
        f = open(self.filePath)
        reader = csv.reader(f)

        firstRow = True
        rowValueList = []
        tableValueList = []
        for row in reader:
            if (firstRow):
                firstRow = False
                self.columnValues = np.array([x for x in row[1:]])                
            else:
                rowValueList.append((row[0]))
                rowDataValues = [x for x in row[1:]]
                tableValueList.append(rowDataValues)
        
        self.rowValues = np.array(rowValueList)
        self.tableValues = np.array(tableValueList)
        
        f.close()
    
    @staticmethod        
    def testTable2DReader(filePath):
        reader = Table2DReader(filePath)
        reader.read()
        print reader.rowValues
        print reader.columnValues
        print reader.tableValues

class CSVReader:
    def __init__(self, filePath, headerRowIndex = 0, firstDataRowIndex = 1):
        self.filePath = filePath
        self.headerRowIndex = headerRowIndex
        self.firstDataRowIndex = firstDataRowIndex
        
    def initialRead(self):
        f = open(self.filePath)
        reader = csv.reader(f)
        tableValues = []
        numRows = 0       
        for row in reader:
            if (numRows == self.headerRowIndex):
                numColumns = len(row[:])
            elif len(row[:]) > numColumns:
                    numColumns = len(row[:])
            numRows += 1
            tableValues.append(row)
#         print (numRows, numColumns, tableValues[0], tableValues[1], tableValues[numRows-1])      
        return (numRows, numColumns, tableValues)
            
    def read(self):
        f = open(self.filePath)
        reader = csv.reader(f)
        rowIndex = 0
        numDataRows = 0
        # determine the structure of the file (numDataRows, numCols, types)
        for row in reader:
            if (rowIndex == self.headerRowIndex):
                columnNames = row[:]
                numColumns = len(row[:])
            elif (rowIndex >= self.firstDataRowIndex):
                if len(row[:]) > numColumns:
                    numColumns = len(row[:])
                numDataRows += 1
            rowIndex += 1
        #TODO derive column types from strings
        storageType = np.dtype([(columnName, np.float64) for columnName in columnNames])
        self.data = np.empty(shape = (numDataRows), dtype = storageType)
        
        f.seek(0)
        rowIndex = 0
        for row in reader:
            if (rowIndex >= self.firstDataRowIndex):
                self.data[rowIndex - self.firstDataRowIndex] = tuple(float(x) for x in row)
            rowIndex += 1
        f.close()
        print("From input file '%s' read %d rows and %d columns"%(self.filePath, numDataRows, numColumns))
        
    @staticmethod
    def test(filePath):
        reader = CSVReader(filePath)
        reader.initialRead()
        
class BatchReader:
    def __init__(self, readerClass, sourceFolder, filter = '*'):
        self.sourceFolder = sourceFolder
        self.filter = filter
        self.fileList = glob.glob(os.path.join(sourceFolder, filter))
        self.i = 0
        self.readerClass = readerClass
    
    def __iter__(self):
        return self

    def next(self):
        if (self.i >= len(self.fileList)):
            raise StopIteration
        else:
            fileName = self.fileList[self.i]
            self.i += 1
            reader = self.readerClass(fileName)
            reader.read()            
            return (fileName, reader.data)

        
if __name__ == "__main__":
    basePath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    print basePath
    #Table2DReader.test(basePath + "StressPressureTemperature/CompositeParallel.csv")
    filepath = os.path.join(basePath, "E149189.csv")
    CSVReader.test(filepath)