from django.template import Library
register = Library()

from smo.model.model import ModelView, NumericalModel, ModelDocumentation

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
def getModelDocUrl(module):
	return "documentation/html/" + module.name + ".html"

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