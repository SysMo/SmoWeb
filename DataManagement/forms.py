'''
Created on Sep 16, 2014

@author: ivaylo
'''
from django import forms

class ImportCSV_Form(forms.Form):
    csvFile = forms.FileField(label='CSV File')
    hdfPath = forms.CharField(label='HDF File Path')
    rowsInDisplay = forms.IntegerField(initial=10,label='Rows to Display')