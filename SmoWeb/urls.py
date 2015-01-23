from django.conf.urls import patterns, include, url
from django.contrib import admin
from SmoWebBase import views

urlpatterns = patterns('',
    url(r'^$', views.router.view),
    url(r'^SmoWebBase/([A-Za-z][A-Za-z0-9_]+)?/?$', views.router.view),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ThermoFluids/', include('ThermoFluids.urls', namespace='ThermoFluids')),
)
