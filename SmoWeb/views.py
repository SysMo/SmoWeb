from django.shortcuts import render_to_response, RequestContext
from smo.model.quantity import Quantities
from smo.django.view import action, ModularPageView, mongoClient
from smo.django.router import ViewRouter, registerView
from smo.model.model import NumericalModel, ModelView, HtmlModule, HtmlBlock, JsBlock
from pymongo import MongoClient
from bson.objectid import ObjectId

router = ViewRouter('SmoWebBase')

class BasePageModule(HtmlModule):
	name = 'BasePageModule'
	label = 'Home'
	block = HtmlBlock(srcType="file", src="HomeBlock.html")
	modelBlocks = [block]

class UnitConverterModule(HtmlModule):
	name = 'UnitConverter'
	label = 'Unit Converter'
	converterHtml = HtmlBlock(srcType="file", src="UnitConverterBlock.html")
	converterJs = JsBlock(srcType="file", src="UnitConverter.js")
	modelBlocks = [converterHtml, converterJs]
	
@registerView(router)
class HomeView(ModularPageView):
	name = "HomeView"
	label = "Home View"
	modules = [BasePageModule, UnitConverterModule]
	
	@action.post()
	def getQuantities(self, parameters, model=None, view= None):
		return Quantities


# from SmoWeb.examples.Tutorial_01_model import AreaCalculator, AreaCalculatorDoc
# class AreaCalculatorView(ModularPageView):
# 	modules = [AreaCalculator, AreaCalculatorDoc]
# 	appName = "AreaCalculator"
# 	controllerName = "AreaCalculatorController"
# 	
# 	def get(self, request):
# 		return render_to_response('ModelViewTemplate.html', {"view": self}, 
# 				context_instance=RequestContext(request))
