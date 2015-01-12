from collections import OrderedDict

class ViewRouter(object):
	"""
	This class creates a global registry of pages. Web pages
	register with an instance (router) using the @registerView
	decorator, and can be served when requested (from router.pages)
	"""
	
	registry = {}
	""" Global registry of routers"""
	
	def __init__(self, name, label = None):
		"""
		:param str name: the name of the router, used as part of the name for the page URL: http::/hostname/routerName/pageName
		"""
		self.name = name
		
		if (label is not None):
			self.label = label
		else:
			self.label = self.name
		
		self.registry[name] = self
		self.pages = OrderedDict()
		
	def view(self, request, name = None):
		"""
		Calls a page view function with name *name* passing the 
		*request* object to it.
		"""
		if (name is None):
			viewInstance = self.pages['HomeView']()	
		elif (name in self.pages):
			viewInstance = self.pages[name]()
		else:
			raise ValueError('No page with name {0}'.format(name))
		
		viewInstance.router = self
		return viewInstance.view(request)


def registerView(router, **kwargs):
	"""
	Class decorator used to register pages to a router
	"""
	def registerViewDecorator(klass):
		if ('path' in kwargs):
			path = kwargs['path']
		else:
			path = klass.name
		router.pages[path] = klass
		return klass
	return registerViewDecorator
