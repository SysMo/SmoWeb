from django.http import JsonResponse
from django.shortcuts import render_to_response, RequestContext
import json
import traceback
import logging
logger = logging.getLogger('django.request.smo.view')

from pymongo import MongoClient
from bson.objectid import ObjectId
mongoClient = MongoClient()

# class SmoJsonResponse(object):
# 	def __enter__(self):
# 		self.exceptionThrown = False
# 		return self
# 	
# 	def __exit__(self, type, value, traceback):
# 		if (value is not None):
# 			self.exceptionThrown = True
# 			self.response = {}
# 			self.response['errStatus'] = True
# 			self.response['error'] = str(value)
# 		return True
# 	
# 	def set(self, response):
# 		if (not self.exceptionThrown):
# 			self.response = response
# 			self.response['errStatus'] = False
# 	
# 	def json(self):
# 		return JsonResponse(self.response)

class Action(object):
	def __init__(self, func):
		self.func = func
		
	def __call__(self, *args, **kwargs):		
		result = self.func(*args, **kwargs)
		return result

class PostAction(Action):
	pass


class action(object):
	@staticmethod
	def post(**kwargs):
		def postActionDecorator(func):
			return PostAction(func)
		return postActionDecorator

class View(object):
	jsLibraries = {
		'dygraph': '/static/dygraph/dygraph-combined.js',
		'dygraphExport': 'http://cavorite.com/labs/js/dygraphs-export/dygraph-extra.js',
		'GoogleAPI': 'https://www.google.com/jsapi',
	}
	template = 'ModelViewTemplate.html'
	def __new__(cls, *args, **kwargs):
		self = object.__new__(cls)
		self._getActions = {}
		self._postActions = {}
		
		for c in reversed(cls.__mro__):
			for key, value in c.__dict__.iteritems():
# 				if (isinstance(value, GetAction)):
# 					self._getActions[key] = value
				if (isinstance(value, PostAction)):
					self._postActions[key] = value
		return self
	
# 	def execGetAction(self, actionName, parameters):
# 		if (actionName in self._getActions.keys()):
# 			return self._getActions[actionName](self, parameters)
# 		else:
# 			raise NameError('No GET action with name {0}'.format(actionName))
	
	def execPostAction(self, actionName, model, view, parameters):
		response = {}
		if (actionName in self._postActions.keys()):
			try:
				response['data'] = self._postActions[actionName](self, model, view, parameters)
				response['errStatus'] = False
			except Exception, e:
				response['errStatus'] = True
				response['error'] = str(e)
				response['stackTrace'] = traceback.format_exc()
		else:
			response['errStatus'] = True
			response['error'] = 'No POST action with name {0}'.format(actionName)
		return JsonResponse(response)
	
	def get(self, request):
		parameters = request.GET
		modelView = None
		self.recordIdDict = {}
		print ('In get')
		if ('model' in parameters):
			modelName = parameters['model']
			# find the active module 
			for module in self.modules:
				if (module.__name__ == modelName):
					self.activeModule = module
					break
			if (self.activeModule is None):
				raise ValueError("Unknown module {0}".format(modelName))
			else:
				if ('view' in parameters):
					# find the active view
					viewName = parameters['view']
					for block in self.activeModule.modelBlocks:
						if (block.name == viewName):
							modelView = block
							break
						if (modelView is None):
							raise ValueError("Unknown view {0} in module {1}".format(viewName, modelName))
					if ('id' in parameters):
						recordId = parameters['id']
						self.recordIdDict[modelView] = recordId
		else:
			print ('Has modules', hasattr(self, 'modules'))
			if (hasattr(self, 'modules') and len(self.modules) > 0):
				self.activeModule = self.modules[0]

		return render_to_response(self.template, {"view": self}, 
						context_instance=RequestContext(request))
	
	def post(self, request):
		postData = json.loads(request.body)
		action = postData['action']
		data = postData['data']
		# Get the action parameters
		parameters = {}
		if ('parameters' in data):
			parameters = data['parameters']
		
		# Get the calling model view  
		model = None
		if ("modelName" in data):
			modelName = data['modelName']
			for module in self.modules:
				if (module.name == modelName):
					model = module
			if (model is None):
				raise ValueError("Unknown model {0}".format(modelName))

		modelView = None
		if (model is not None and "viewName" in data):
			viewName = data['viewName']
			for block in model.modelBlocks:
				if (block.name == viewName):
					modelView = block
			if (modelView is None):
				raise ValueError("Unknown model view {0}.{1}".format(modelName, viewName))
		
		logger.debug('Action: ' + action)
		logger.debug('Parameters: ' + json.dumps(parameters))
		return self.execPostAction(action, model, modelView, parameters)
		
	
	@action.post()
	def load(self, model, view, parameters):
		self = model()
		
		if 'recordId' in parameters:
			recordId = parameters['recordId']
			id = ObjectId(recordId)
			db = mongoClient.SmoWeb
			coll = db.savedInputs
			conf = coll.find_one({'_id': id})
			if (conf is not None):
				self.fieldValuesFromJson(conf['values'])
			else: 
				raise ValueError("Unknown record with id: {0}".format(recordId))
		return self.modelView2Json(view)
		
	@action.post()
	def compute(self, model, view, parameters):
		instance = model()
		instance.fieldValuesFromJson(parameters)
		instance.compute()
		return instance.modelView2Json(view)
	
	@action.post()
	def save(self, model, view, parameters):
		instance = model()
		instance.fieldValuesFromJson(parameters)
		db = mongoClient.SmoWeb
		coll = db.savedInputs
		id = coll.insert(instance.modelView2Json(view))
		return {'model': model.name, 'view': view.name, 'id' : str(id)}	
	
	@classmethod
	def asView(cls):
		def view(request):
			self = cls()
			if request.method == 'GET':
				logger.debug('GET ' + request.path)
				return self.get(request)
			elif request.method == 'POST':
				logger.debug('POST ' + request.path)
				return self.post(request)
			else:
				raise ValueError('Only GET and POST requests can be served')
				
		return view
	

def test():
	class MyView(View):
		def get(self):
			return 10 
		@action('post')
		def add(self, parameters):
			return 42
	class Req(object):
		pass
	request = Req()
	request.method = 'POST'
	request.body = '{"action": "add", "parameters": {}}'
	print MyView.asView()(request)

if __name__ == '__main__':
	test()
