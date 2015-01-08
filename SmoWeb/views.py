from django.shortcuts import render_to_response, RequestContext
from smo.model.quantity import Quantities
from smo.django.view import action, View, mongoClient

from pymongo import MongoClient
from bson.objectid import ObjectId

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
	
# 	modelName: $scope.modelName, 
# 	viewName: $scope.viewName, 
# 	parameters: {recordId: $scope.recordId}
	
	def get(self, request):
		parameters = request.GET
		
		modelName = None
		viewName = None
		recordId = None
		
		if ('model' in parameters):
			modelName = parameters['model']
		if ('view' in parameters):
			viewName = parameters['view']
		if ('id' in parameters):
			recordId = parameters['id']
		
		self.activeModule = None
		self.recordIdDict = None
		
		if (modelName is not None) and (viewName is not None) and (recordId is not None):
			for module in self.modules:
				if (module.__name__ == modelName):
					self.activeModule = module
			if (self.activeModule is None):
				raise ValueError("Unknown model {0}".format(modelName))	
			
			id = ObjectId(recordId)
			db = mongoClient.SmoWeb
			coll = db.savedInputs
			conf = coll.find_one({'_id': id})
			if (conf is None):
				raise ValueError("Unknown record with id: {0}".format(recordId))
			
			for view in self.activeModule.modelBlocks:
				if (view.name == viewName):
					self.recordIdDict = {view : recordId}
			if (self.recordIdDict is None):
				raise ValueError("Unknown view {0}".format(viewName))	
		
		elif (modelName is None) and (viewName is None) and (recordId is None):
			self.activeModule = self.modules[0]
			self.recordIdDict = {}
		else:		
			raise ValueError("GET parameters should be 'model' and 'view' and 'id'")	
		
		return render_to_response('ModelViewTemplate.html', {"view": self}, 
				context_instance=RequestContext(request))
