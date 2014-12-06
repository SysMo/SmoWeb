'''
Created on Sep 10, 2014

@author: nasko
'''
from django.conf.urls import patterns, url
from ThermoFluids import views

urlpatterns = patterns('',
    url(r'^FluidPropsCalculator/$', views.FluidPropsCalculatorView.asView(), name='FluidPropsCalculator'),
    url(r'^FlowResistance/', views.FlowResistanceView.asView(), name='FlowResistance'),
	url(r'^HeatPump/', views.heatPumpView, name='HeatPump'),
    url(r'^FreeConvection/', views.freeConvectionView, name='FreeConvection'),
	url(r'^TestView/', views.testView, name='testView'),
	url(r'^HeatExchange1D/', views.HeatExchange1DView.asView(), name='HeatExchange1D'),
)
