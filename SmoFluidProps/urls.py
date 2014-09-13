'''
Created on Sep 10, 2014

@author: nasko
'''
from django.conf.urls import patterns, url
from SmoFluidProps import views

urlpatterns = patterns('',
    url(r'^SetUp/$', views.FluidProps_SetUpView.as_view(), name='FluidProps_SetUp'),
#    url(r'^SetUP/(?P<fluidPropsId>\d+)/$', views.FluidProps_SetUpView.as_view(), name='FluidProps_SetUpWithArgs')
)
