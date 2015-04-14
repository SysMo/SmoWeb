from django.http import JsonResponse
from django.shortcuts import render_to_response, RequestContext
from SmoWeb.settings import JINJA_TEMPLATE_IMPORTS
import json
import traceback
import logging
logger = logging.getLogger('django.request.smo.view')

from pymongo import MongoClient
from bson.objectid import ObjectId

mongoClient = MongoClient()

class Action(object):
	"""
	Abstract base class for all action types
	"""
	def __init__(self, func):
		self.func = func
		
	def __call__(self, *args, **kwargs):		
		result = self.func(*args, **kwargs)
		return result

class PostAction(Action):
	"""
	General POST action
	"""

class action(object):
	@staticmethod
	def post(**kwargs):
		def postActionDecorator(func):
			action = PostAction(func)
			action.label = ""
			if (func.__doc__ is not None):
				action.label = func.__doc__
			return action
		return postActionDecorator

class ModularPageViewMeta(type):
	"""
	Metaclass facilitation the creation of modular page views	
	"""
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		if ('controllerName' not in attrs):
			attrs['controllerName'] = name + 'Controller'
		# Containers to collect actions, library and module names
		postActions = {}
		requiredJSLibraries = set()
		requiredGoogleModules = set()

		new_class = (super(ModularPageViewMeta, cls)
			.__new__(cls, name, bases, attrs))

		for c in reversed(new_class.__mro__):
			for key, value in c.__dict__.iteritems():
				if (isinstance(value, PostAction)):
					postActions[key] = value
				elif (key == 'requireJS'):
					requiredJSLibraries.update(c.requireJS)
				elif (key == 'requireGoogle'):
					requiredGoogleModules.update(c.requireGoogle)
		
		if (len(requiredGoogleModules) > 0):
			requiredJSLibraries.update(['GoogleAPI'])
		
		if (new_class.__doc__ is None):
			new_class.__doc__  = ""
		
		new_class.__doc__ += '\n' + ''.join(
			['		* :attr:`{0}`: {1}\n'.format(name, action.label.strip()) for name, action in postActions.iteritems()]
		)
		
		new_class.postActions = postActions
		new_class.requiredJSLibraries = requiredJSLibraries
		new_class.requiredGoogleModules = requiredGoogleModules
		
		return new_class
	
class ModularPageView(object):
	"""
	Abstract base class for creating pages consisting of modules. There are different kind of modules:
		* NumericalModel model-views
		* Restructured text views
		* HTML module views
		
	:param: :class:`smo.web.router.ViewRouter` router: a router instance with which the view is registered 
		
	Class attributes:
		* :attr:`label`: label for the page view class (default is the page view class name)
		* :attr:`controllerName`: name of the AngularJS contoller for the page view (default is the page view class name + 'Controller')
		* :attr:`modules`: modules making up the page view
		* :attr:`injectVariables`: list of names of AngularJS dependencies required for the page view
		* :attr:`jsLibraries`: registry of common Java Script libraries used in the applicaions
		* :attr:`googleModules`:  registry of common Google modules used in the applicaions
		* :attr:`requireJS`: list of JS libraries required by the page view
		* :attr:`requireGoogle`: list of Google modules required by the page view
		* :attr:`template`: HTML template file
		
	Defined POST actions:"""
		
	__metaclass__ = ModularPageViewMeta
	
	jsLibraries = {
		'dygraph': '/static/dygraph/dygraph-combined.js',
		'dygraphExport': 'http://cavorite.com/labs/js/dygraphs-export/dygraph-extra.js',
		'MathJax': "http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML",
		'GoogleAPI': 'https://www.google.com/jsapi'
	}
	
	googleModules = {
		'visualization':{'version': '1.0', 'packages': ["corechart", "table", "controls"]}
	}

	requireJS = ['MathJax']
	requireGoogle = []
	template = 'SmoWebBase/ModelViewTemplate.jinja'
	
	def __init__(self, router):
		self.router = router
		
	def view(self, request):
		"""
		Entry function for processing an HTTP request
		"""
		if request.method == 'GET':
			logger.debug('GET ' + request.path)
			return self.get(request)
		elif request.method == 'POST':
			logger.debug('POST ' + request.path)
			return self.post(request)
		else:
			raise ValueError('Only GET and POST requests can be served')

	def get(self, request):
		"""
		Function handling HTTP GET request
		"""
		parameters = request.GET
		modelView = None
		self.recordIdDict = {}
		if (hasattr(self, 'modules') and len(self.modules) > 0):
			self.activeModule = None
		else:
			raise ValueError('This page defines no modules')
		
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
			self.activeModule = self.modules[0]
		
		context = {"pageView": self}
		context.update(JINJA_TEMPLATE_IMPORTS)
		context[self.router.name] = self.router.appNamespace
		return render_to_response(self.template, context, 
						context_instance=RequestContext(request))
	
	def post(self, request):
		"""
		Function handling HTTP POST request
		"""
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
				if (module.__name__ == modelName):
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
	
		
	def execPostAction(self, actionName, model, view, parameters):
		"""
		Executes a specific POST action registered with this view
		"""
		response = {}
		if (actionName in self.postActions.keys()):
			try:
				response['data'] = self.postActions[actionName](self, model, view, parameters)
				response['errStatus'] = False
			except Exception, e:
				response['errStatus'] = True
				response['error'] = str(e)
				response['stackTrace'] = traceback.format_exc()
		else:
			response['errStatus'] = True
			response['error'] = 'No POST action with name {0}'.format(actionName)
		return JsonResponse(response)
	
	@action.post()
	def load(self, model, view, parameters):
		"""
		Action for loading model data
		"""
		instance = model()
		if 'viewRecordId' in parameters:
			viewRecordId = parameters['viewRecordId']
			db = mongoClient.SmoWeb
			coll = db.savedViewData
			record = coll.find_one({'_id': ObjectId(viewRecordId)})
			if (record is not None):
				instance.fieldValuesFromJson(record['values'])
			else: 
				raise ValueError("Unknown view data record with id: {0}".format(viewRecordId))
		return instance.modelView2Json(view)
		
	@action.post()
	def save(self, model, view, parameters):
		"""
		Action for saving data in the DB
		"""
		db = mongoClient.SmoWeb
		coll = db.savedViewData
		recordId = coll.insert({'values' : parameters})
		return {'model': model.__name__, 'view': view.name, 'id' : str(recordId)}
		
	@action.post()
	def compute(self, model, view, parameters):
		"""
		Predefined compute action
		"""
		instance = model()
		instance.fieldValuesFromJson(parameters)
		instance.compute()
		return instance.modelView2Json(view)
	
	@action.post()
	def loadEg(self, model, view, parameters):
		instance = model()
		print parameters
		getattr(instance, parameters)()
		return instance.modelView2Json(view)
				
	@classmethod
	def asView(cls):
		"""
		Can be used if a function-like object is needed instead of
		a class instance.
		"""
		def view(request):
			instance = cls()
			return instance.view(request)
		return view

if __name__ == '__main__':
	pass
