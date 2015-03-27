'''
Created on Sep 16, 2014

@author: ivaylo
'''
from django.conf.urls import patterns, url
from DataManagement import views

urlpatterns = patterns('',
    url(r'^([A-Za-z][A-Za-z0-9_]+)/$', views.router.view)
)