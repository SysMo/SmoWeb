from django.template import Library
register = Library()

from smo.model.model import ModelView

@register.filter(name = 'isModelView')
def isModelView(obj):
	result = isinstance(obj, ModelView)
	print result
	return result

