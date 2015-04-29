'''
Created on Sep 10, 2014

@author: nasko
'''
from django.conf.urls import patterns, url
from ThermoFluids import views

urlpatterns = patterns('',
	url(r'^([A-Za-z][A-Za-z0-9_]+)?/?$', views.router.view)
)
