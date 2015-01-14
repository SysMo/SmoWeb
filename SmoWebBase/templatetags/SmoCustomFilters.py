from django.template import Library
from SmoWeb.settings import BASE_DIR

register = Library()

@register.filter
def isBase(routerName):
	return routerName == 'SmoWebBase'

from smo.model.model import ModelView, NumericalModel, ModelDocumentation, HtmlModule, HtmlSection
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
def isHtmlModule(obj):
	return isinstance(obj, HtmlModule)

@register.filter
def isHtmlSection(obj):
	return isinstance(obj, HtmlSection)

@register.filter
def isSrcFile(module):
	return module.srcType == 'file'

@register.filter
def getHtmlSectionUrl(block, pageView):
	return BASE_DIR + "/" + pageView.router.name + "/templates/" + pageView.router.name + "/blocks/" + block.src


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

@register.filter
def classDir(obj):
	return dir(obj)