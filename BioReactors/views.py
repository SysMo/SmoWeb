from smo.web.view import ModularPageView
from smo.web.view import action
from smo.web.router import ViewRouter, registerView
import BioReactors

router = ViewRouter('BioReactors', BioReactors)

from BioReactors.models.SimpleChemostatModel import SimpleChemostatModel, SimpleChemostatDoc 
@registerView(router)
class SimpleGradostatView(ModularPageView):
    label = 'Simple Gradostat'
    modules = [SimpleChemostatModel, SimpleChemostatDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']
    