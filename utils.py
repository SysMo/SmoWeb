'''
Created on Sep 17, 2014

@author: ivaylo
'''
import csv
import numpy as np
import glob
import os

def handle_uploaded_file(f, media_path):
    destination = open(os.path.join(media_path, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return destination
    
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
#             tableValues.append([float(elem) for elem in row])
#         print (numRows, numColumns, tableValues[0], tableValues[1], tableValues[numRows-1])      
        return {'numRows': numRows, 'numColumns': numColumns, 'tableValues': tableValues}
    
    @staticmethod
    def test(filePath):
        reader = CSVReader(filePath)
        reader.initialRead()
