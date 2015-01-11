from collections import OrderedDict

class ViewRouter(object):
	"""
	This class creates a global registry of pages. Web pages
	register with an instance (router) using the @registerView
	decorator, and can be served when requested (from router.pages)
	"""
	
	registry = {}
	""" Global registry of routers"""
	
	def __init__(self, name):
		"""
		:param str name: the name of the router, used as part of the name for the page URL: http::/hostname/routerName/pageName
		"""
		self.name = name
		self.registry[name] = self
		self.pages = OrderedDict()
		
	def view(self, request, name):
		"""
		Calls a page view function with name *name* passing the 
		*request* object to it.
		"""
		if (name in self.pages):
			viewInstance = self.pages[name]()
			viewInstance.router = self
			return viewInstance.view(request)
		else:
			raise ValueError('No page with name {0}'.format(name))


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
