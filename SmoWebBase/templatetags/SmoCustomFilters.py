from django.template import Library
register = Library()
from SmoWeb.views import HomeView

@register.filter
def isBase(routerName):
	return routerName == 'SmoWebBase'

from smo.model.model import ModelView, NumericalModel, ModelDocumentation, HtmlPageModule
@register.filter
def isModelView(obj):
	return isinstance(obj, ModelView)

@register.filter
def isNumericalModel(obj):
	return isinstance(obj, NumericalModel)

@register.filter
def isModelDocumentation(obj):
	return isinstance(obj, ModelDocumentation)

@register.filter
def isHtmlPage(obj):
	return isinstance(obj, HtmlPageModule)

@register.filter
def getModelDocUrl(module):
	return "documentation/html/" + module.name + ".html"

@register.filter
def getHtmlPageUrl(module, pageView):
	return module.__class__.src

@register.filter
def isSrcFile(module):
	return module.__class__.srcType == 'file'

@register.filter
def isSrcString(module):
	return module.__class__.srcType == 'string'

@register.filter
def isActive(view, module):
	if (isinstance(module, type)):
		return view.activeModule == module
	else:
		return  view.activeModule == module.__class__

@register.filter
def getItem(dictionary, key):
	if (dictionary.get(key) is not None):
		return dictionary.get(key)
	else:
		return ""

@register.filter
def toStr(obj):
	return obj.__str__()