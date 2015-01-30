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
    
from smo.model.model import *
from smo.model.fields import *
from smo.model.actions import *

class AreaCalculator(NumericalModel):
    name = "AreaCalculator"
    label = "Area Calculator"
    figure = ModelFigure(src="img/Calculator.png", height=150, width=250)
    description = ModelDescription("A calculator of a rectangle's area", show = True)
    showOnHome = False
    
    ############# Inputs ###############
    # Fields
    width = Quantity('Length')
    length = Quantity('Length')
    geometryIn = FieldGroup([width, length], label = "Geometry")

    inputs = SuperGroup([geometryIn], label = "Inputs")
    
    # Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    # Model view
    inputView = ModelView(ioType = "input", superGroups = [inputs], 
        actionBar = inputActionBar, autoFetch = True)
    
    
    ############# Results ###############
    # Fields
    area = Quantity('Area')
    geometryOut = FieldGroup([area], label = "Geometry")
    
    results = SuperGroup([geometryOut], label = "Results")
    
    # Model view
    resultView = ModelView(ioType = "output", superGroups = [results])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    ############# Methods ################
    def compute(self):
        self.area = self.width * self.length

       
@registerView(router)
class HomeView(ModularPageView):
    name = "HomeView"
    label = "Home View"
    injectVariables = ['ModelCommunicator', 'variables']
    modules = [BasePageModule, UnitConverterModule, Company, People, AreaCalculator]
    
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