from django.conf.urls import patterns, include, url
from django.contrib import admin
from SmoWeb import views

urlpatterns = patterns('',
    url(r'^$', views.HomeView.asView(), name='Home' ),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ThermoFluids/', include('ThermoFluids.urls', namespace='ThermoFluids')),
    url(r'^DataManagement/', include('DataManagement.urls', namespace='DataManagement')),
    url(r'^UnitConverter/', views.unitConverterView.asView(), name='UnitConverter'),
    url(r'^examples/AreaCalculatorView', views.AreaCalculatorView.asView(), name = "Example_AreaCalculatorView")
)
