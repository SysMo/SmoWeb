from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SmoWeb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'SmoWeb.views.home', name='home' ),
    url(r'^platform/', 'SmoWeb.views.platform', name='platform'),
    url(r'^SmoFluidProps/', include('SmoFluidProps.urls', namespace = 'SmoFluidProps')),
    url(r'^admin/', include(admin.site.urls)),
)
