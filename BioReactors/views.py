from smo.web.view import ModularPageView
from smo.web.view import action
from smo.web.router import ViewRouter, registerView
import BioReactors

router = ViewRouter('BioReactors', BioReactors)

from .models import SimpleChemostatModel, SimpleChemostatDoc 
@registerView(router)
class SimpleChemostatView(ModularPageView):
    label = 'Simple Chemostat'
    modules = [SimpleChemostatModel, SimpleChemostatDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']
    
from .models import AnaerobicDigestionDDEModel, AnaerobicDigestionDDEDoc 
@registerView(router)
class AnaerobicDigestionDDEView(ModularPageView):
    label = 'Anaerobic Digestion (DDE)'
    modules = [AnaerobicDigestionDDEModel, AnaerobicDigestionDDEDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']