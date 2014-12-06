import json
from django.http import JsonResponse

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
		for key, value in cls.__dict__.iteritems():
			if (isinstance(value, GetAction)):
				instance._getActions[key] = value
			elif (isinstance(value, PostAction)):
				instance._postActions[key] = value
		return instance
	def execGetAction(self, actionName, parameters):
		if (actionName in self._getActions.keys()):
			self._getActions[actionName](self, parameters)
		else:
			raise NameError('No GET action with name {0}'.format(actionName))
	def execPostAction(self, actionName, parameters):
		if (actionName in self._postActions.keys()):
			self._postActions[actionName](self, parameters)
		else:
			raise NameError('No POST action with name {0}'.format(actionName))
	@classmethod
	def asView(cls):
		def view(request):
			instance = cls()
			if request.method == 'GET':
				if ('get' in cls.__dict__):
					return instance.get()
				else:
					raise NotImplementedError(
						'View {0} can not serve GET request'.format(cls.__name__))
			elif request.method == 'POST':
				if ('post' in cls.__dict__):
					return instance.post()
				else:
					postData = json.loads(request.body)
					action = postData['action']
					parameters = postData['parameters']
					return instance.execPostAction(action, parameters)
				
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