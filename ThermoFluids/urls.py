'''
Created on Sep 10, 2014

@author: nasko
'''
from django.conf.urls import patterns, url
from ThermoFluids import views

urlpatterns = patterns('',
    url(r'^FluidPropertiesCoolProp/$', views.FluidPropertiesCoolPropView.as_view(), name='FluidPropertiesCoolProp'),
    url(r'^TestView/', views.testView, name='testView'), 
#    url(r'^SetUP/(?P<fluidPropsId>\d+)/$', views.FluidProps_SetUpView.as_view(), name='FluidProps_SetUpWithArgs')
)
