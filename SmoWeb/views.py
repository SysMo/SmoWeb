import json
from django.shortcuts import render_to_response, RequestContext
from django.http import JsonResponse
from smo.model.quantity import Quantities
from smo.django.view import action, View

class HomeView(View):
    def get(self, request):
        return render_to_response('Base.html', locals(), 
                context_instance=RequestContext(request))
        
class unitConverterView(View):
    def get(self, request):
        return render_to_response('UnitConverter.html', locals(), 
                context_instance=RequestContext(request))
        
    @action('post')
    def getQuantities(self, parameters):
        return Quantities