from smo.model.quantity import Quantities
from smo.django.view import action, ModularPageView
from smo.django.router import ViewRouter, registerView
from smo.model.model import HtmlModule, HtmlBlock, JsBlock, RestModule
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
 
class Company(RestModule):
    label = "Company"

class Team(RestModule):
    label = 'Our Team'
    

class Platform(RestModule):
    label = "Platform"
       
@registerView(router)
class HomeView(ModularPageView):
    label = "Home View"
    injectVariables = ['ModelCommunicator', 'variables']
    modules = [HomeModule, UnitConverter, Company, Team, Platform]
    
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
