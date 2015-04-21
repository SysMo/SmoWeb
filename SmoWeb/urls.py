from django.conf.urls import patterns, include, url
from django.contrib import admin
from SmoWebBase import views
from django.conf import settings

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', views.router.view),
    url(r'^SmoWebBase/Export/?$', views.export),
    url(r'^SmoWebBase/([A-Za-z][A-Za-z0-9_]+)?/?$', views.router.view),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ThermoFluids/', include('ThermoFluids.urls', namespace='ThermoFluids')),
    url(r'^BioReactors/', include('BioReactors.urls', namespace='BioReactors'))
)
