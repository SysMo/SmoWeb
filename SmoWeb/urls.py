from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SmoWeb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'SmoWeb.views.home', name='home' ),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^Platform/', 'SmoWeb.views.platform', name='platform'),
    url(r'^ThermoFluids/', include('ThermoFluids.urls', namespace='ThermoFluids')),
    url(r'^DataManagement/', include('DataManagement.urls', namespace='DataManagement')), 
)
