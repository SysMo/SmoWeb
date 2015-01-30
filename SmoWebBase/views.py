from smo.model.quantity import Quantities
from smo.django.view import action, ModularPageView
from smo.django.router import ViewRouter, registerView
from smo.model.model import HtmlModule, HtmlBlock, JsBlock, RestBlock
import SmoWebBase

router = ViewRouter('SmoWebBase', SmoWebBase)

class BasePageModule(HtmlModule):
    name = 'BasePageModule'
    label = 'Home'
    block = HtmlBlock(srcType="file", src="HomeBlock.jinja")
    modelBlocks = [block]

class UnitConverterModule(HtmlModule):
    name = 'UnitConverter'
    label = 'Unit Converter'
    converterHtml = HtmlBlock(srcType="file", src="UnitConverterBlock.html")
    converterJs = JsBlock(srcType="file", src="UnitConverter.js")
    modelBlocks = [converterHtml, converterJs]
 
class Company(RestBlock):
    name = 'Company'
    label = 'Company'

class People(RestBlock):
    name = 'People'
    label = 'People'
       
@registerView(router)
class HomeView(ModularPageView):
    name = "HomeView"
    label = "Home View"
    injectVariables = ['ModelCommunicator', 'variables']
    modules = [BasePageModule, UnitConverterModule, Company, People]
    
    @action.post()
    def getQuantities(self, parameters, model=None, view= None):
        return Quantities

class Industries(RestBlock):
    name = 'Industries'
    label = 'Industries'
    
class Products(RestBlock):
    name = 'Products'
    label = 'Products'
    
class Services(RestBlock):
    name = 'Services'
    label = 'Services'

@registerView(router)
class SysmoView(ModularPageView):
    name = "Sysmo"
    label = "SysMo Ltd"
    modules = [Industries, Products, Services]