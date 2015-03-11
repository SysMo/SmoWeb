from django.conf.urls import patterns, url
from BioReactors import views

urlpatterns = patterns('',
    url(r'^([A-Za-z][A-Za-z0-9_]+)?/?$', views.router.view)
)