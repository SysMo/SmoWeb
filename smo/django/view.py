import json
from django.http import JsonResponse
import traceback
import logging
logger = logging.getLogger('django.request.smo.view')

class SmoJsonResponse(object):
	def __enter__(self):
		self.exceptionThrown = False
		return self
	
	def __exit__(self, type, value, traceback):
		if (value is not None):
			self.exceptionThrown = True
			self.response = {}
			self.response['errStatus'] = True
			self.response['error'] = str(value)
		return True
	
	def set(self, response):
		if (not self.exceptionThrown):
			self.response = response
			self.response['errStatus'] = False
	
	def json(self):
		return JsonResponse(self.response)

class Action(object):
	def __init__(self, func):
		self.func = func
		
	def __call__(self, *args, **kwargs):		
		result = self.func(*args, **kwargs)
		return result

class GetAction(Action):
	pass

class PostAction(Action):
	pass

def action(actionType):
	def getActionDecorator(func):
		return GetAction(func)
	def postActionDecorator(func):
		return PostAction(func)
	if (actionType == 'get'):
		return getActionDecorator
	elif (actionType == 'post'):
		return postActionDecorator
	else:
		raise TypeError('Unknown action type: {0}'.format(actionType))

class View(object):
	def __new__(cls, *args, **kwargs):
		instance = object.__new__(cls)
		instance._getActions = {}
		instance._postActions = {}
		
		for c in reversed(cls.__mro__):
			for key, value in c.__dict__.iteritems():
				if (isinstance(value, GetAction)):
					instance._getActions[key] = value
				elif (isinstance(value, PostAction)):
					instance._postActions[key] = value
		return instance
	
	def execGetAction(self, actionName, parameters):
		if (actionName in self._getActions.keys()):
			return self._getActions[actionName](self, parameters)
		else:
			raise NameError('No GET action with name {0}'.format(actionName))
	
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
	
	@action('post')
	def load(self, model, view, parameters):
		instance = model()
		return instance.modelView2Json(view)
		
	@action('post')
	def compute(self, model, view, parameters):
		instance = model()
		instance.fieldValuesFromJson(parameters)
		instance.compute()
		return instance.modelView2Json(view)
	
	@classmethod
	def asView(cls):
		def view(request):
			instance = cls()
			if request.method == 'GET':
				logger.debug('GET ' + request.path)
				if ('get' in cls.__dict__):
					return instance.get(request)
				else:
					raise NotImplementedError(
						'View {0} can not serve GET request'.format(cls.__name__))
			elif request.method == 'POST':
				logger.debug('POST ' + request.path)
				if ('post' in cls.__dict__):
					return instance.post(request)
				else:
					postData = json.loads(request.body)
					action = postData['action']
					data = postData['data']
					
					# Get the model and view calling 
					model = None
					if ("modelName" in data):
						modelName = data['modelName']
						for module in instance.modules:
							if (module.name == modelName):
								model = module
						if (model is None):
							raise ValueError("Unknown model {0}".format(modelName))

					view = None
					if (model is not None and "viewName" in data):
						viewName = data['viewName']
						for modelView in model.modelBlocks:
							if (modelView.name == viewName):
								view = modelView
						if (view is None):
							raise ValueError("Unknown model view {0}.{1}".format(modelName, viewName))
					
					parameters = {}
					if ('parameters' in data):
						parameters = data['parameters']
					logger.debug('Action: ' + action)
					logger.debug('Parameters: ' + json.dumps(parameters))
					return instance.execPostAction(action, model, view, parameters)
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