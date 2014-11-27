'''
Created on Sep 10, 2014

@author: nasko
'''
from django.conf.urls import patterns, url
from ThermoFluids import views

urlpatterns = patterns('',
    url(r'^FluidPropsCalculator/$', views.fluidPropsCalculatorView, name='FluidPropsCalculator'),
    url(r'^FlowResistance/', views.flowResistanceView, name='FlowResistance'),
	url(r'^HeatPump/', views.heatPumpView, name='HeatPump'),
    url(r'^FreeConvection/', views.freeConvectionView, name='FreeConvection'),
	url(r'^TestView/', views.testView, name='testView'),
)
