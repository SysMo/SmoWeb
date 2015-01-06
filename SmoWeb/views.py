from django.shortcuts import render_to_response, RequestContext
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

from SmoWeb.examples.Tutorial_01_model import AreaCalculator, AreaCalculatorDoc
class AreaCalculatorView(View):
	modules = [AreaCalculator, AreaCalculatorDoc]
	appName = "AreaCalculator"
	controllerName = "AreaCalculatorController"
	
	def get(self, request):
		AreaCalculator.active = True
		return render_to_response('ModelViewTemplate.html', {"view": self}, 
				context_instance=RequestContext(request))
	
	@action('post')
	def compute(self, parameters):
		calc = AreaCalculator()
		calc.fieldValuesFromJson(parameters)
		calc.compute()
		return calc.modelView2Json(calc.resultView)