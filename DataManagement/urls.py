'''
Created on Sep 16, 2014

@author: ivaylo
'''
from django.conf.urls import patterns, url
from DataManagement import views

urlpatterns = patterns('',
    url(r'^ImportCSV/$', views.importCSV, name='ImportCSV'),
    url(r'^CSVtoHDF/$', views.CSVtoHDF, name='CSVtoHDF'),
    url(r'^HdfInterface/$', views.hdfInterfaceView, name='hdfInterfaceView'),
)