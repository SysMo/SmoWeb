'''
Created on Sep 10, 2014

@author: nasko
'''
from django.conf.urls import patterns, url
from ThermoFluids import views

urlpatterns = patterns('',
	url(r'StartJob', views.start_job),
	url(r'CheckProgress', views.check_progress),
	url(r'^([A-Za-z][A-Za-z0-9_]+)?/?$', views.router.view)
)
