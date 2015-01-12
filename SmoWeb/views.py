from django.shortcuts import render_to_response, RequestContext
from smo.model.quantity import Quantities
from smo.django.view import action, ModularPageView, mongoClient
from smo.django.router import ViewRouter, registerView

from pymongo import MongoClient
from bson.objectid import ObjectId

router = ViewRouter('Base')

@registerView(router)
class HomeView(ModularPageView):
	name = "HomeView"
	label = "Home View"

# 	def get(self, request):
# 		return render_to_response('Base.html', locals(), 
# 				context_instance=RequestContext(request))
		
# class unitConverterView(ModularPageView):
# 	def get(self, request):
# 		return render_to_response('UnitConverter.html', locals(), 
# 				context_instance=RequestContext(request))
# 		
# 	@action.post()
# 	def getQuantities(self, parameters):
# 		return Quantities

# from SmoWeb.examples.Tutorial_01_model import AreaCalculator, AreaCalculatorDoc
# class AreaCalculatorView(ModularPageView):
# 	modules = [AreaCalculator, AreaCalculatorDoc]
# 	appName = "AreaCalculator"
# 	controllerName = "AreaCalculatorController"
# 	
# 	def get(self, request):
# 		return render_to_response('ModelViewTemplate.html', {"view": self}, 
# 				context_instance=RequestContext(request))
