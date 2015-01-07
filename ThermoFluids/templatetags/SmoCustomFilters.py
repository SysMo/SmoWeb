from django.template import Library
register = Library()

from smo.model.model import ModelView, NumericalModel

@register.filter
def isModelView(obj):
	return isinstance(obj, ModelView)

@register.filter
def isNumericalModel(obj):
	return isinstance(obj, NumericalModel)

@register.filter
def isActive(view, module):
	if (isinstance(module, type)):
		return view.activeModule == module
	else:
		return  view.activeModule == module.__class__

@register.filter
def getItem(dictionary, key):
	return dictionary.get(key)

@register.filter
def toStr(obj):
	return obj.__str__()