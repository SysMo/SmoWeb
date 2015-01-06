from django.template import Library
register = Library()

from smo.model.model import ModelView, NumericalModel

@register.filter(name = 'isModelView')
def isModelView(obj):
	return isinstance(obj, ModelView)

@register.filter(name = 'isNumericalModel')
def isNumericalModel(obj):
	return isinstance(obj, NumericalModel)