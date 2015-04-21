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
    injectVariables = ['communicator', 'quantities']
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

from django.http import HttpResponse
def export(request):
    data = request.POST["data"]
    option = request.POST["exportOption"]
    
    if (option == 'csv'):
        import csv
        arr = data.split("\n")
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="table.csv"'
        writer = csv.writer(response)
        for row in arr:
            writer.writerow(row.split(','))
    elif (option == 'json'):
        data = data.replace("'", '"')
        response = HttpResponse(data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="inputs.dat"'
    else:
        raise ValueError('Unimplemented export option')
    
    return response