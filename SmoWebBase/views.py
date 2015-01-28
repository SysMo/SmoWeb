from smo.model.quantity import Quantities
from smo.django.view import action, ModularPageView
from smo.django.router import ViewRouter, registerView
from smo.model.model import HtmlModule, HtmlBlock, JsBlock
import SmoWebBase

router = ViewRouter('SmoWebBase', SmoWebBase)

class BasePageModule(HtmlModule):
    name = 'BasePageModule'
    label = 'Home'
    block = HtmlBlock(srcType="file", src="HomeBlock.jinja")
    modelBlocks = [block]
    
class AboutUs(HtmlModule):
    name = 'AboutUs'
    label = 'About Us'
    block = HtmlBlock(srcType="file", src="AboutUs.html")
    modelBlocks = [block]

class UnitConverterModule(HtmlModule):
    name = 'UnitConverter'
    label = 'Unit Converter'
    converterHtml = HtmlBlock(srcType="file", src="UnitConverterBlock.html")
    converterJs = JsBlock(srcType="file", src="UnitConverter.js")
    modelBlocks = [converterHtml, converterJs]
    
@registerView(router)
class HomeView(ModularPageView):
    name = "HomeView"
    label = "Home View"
    injectVariables = ['ModelCommunicator', 'variables']
    modules = [BasePageModule, UnitConverterModule, AboutUs]
    
    @action.post()
    def getQuantities(self, parameters, model=None, view= None):
        return Quantities
