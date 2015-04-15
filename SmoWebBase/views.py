from smo.model.quantity import Quantities
from smo.web.view import action, ModularPageView
from smo.web.router import ViewRouter, registerView
from smo.web.modules import HtmlModule, RestModule
from smo.web.blocks import HtmlBlock, JsBlock
import SmoWebBase

router = ViewRouter('SmoWebBase', SmoWebBase)

### Home-page view
class HomeModule(HtmlModule):
    label = 'Home'
    block = HtmlBlock(srcType="file", src="HomeBlock.jinja")
    modelBlocks = [block]

class UnitConverter(HtmlModule):
    label = 'Unit Converter'
    converterHtml = HtmlBlock(srcType="file", src="UnitConverterBlock.html")
    converterJs = JsBlock(srcType="file", src="UnitConverter.js")
    modelBlocks = [converterHtml, converterJs]
 
class Platform(RestModule):
    label = "Platform"
    
class License(RestModule):
    label = "License"

class Company(RestModule):
    label = "Company"

class Team(RestModule):
    label = 'Our Team'
    

class Testimonials(RestModule):
    label = "Testimonials"

class Disclaimer(HtmlModule):
    label = "Disclaimer"
    block = HtmlBlock(srcType="file", src="Disclaimer.html")
    modelBlocks = [block]
       
@registerView(router)
class HomeView(ModularPageView):
    label = "Home View"
    injectVariables = ['ModelCommunicator', 'quantities']
    modules = [HomeModule, UnitConverter, Platform, License, Company, Team, Testimonials, Disclaimer]
    
    @action.post()
    def getQuantities(self, parameters, model=None, view= None):
        return Quantities

### Sysmo page view
class Industries(RestModule):
    label = "Industries"
    
class Products(RestModule):
    label = "Products"
    
class Services(RestModule):
    label = "Services"

@registerView(router)
class SysmoView(ModularPageView):
    label = "SysMo Ltd"
    modules = [Products, Services, Industries]