from smo.web.view import ModularPageView
from smo.web.view import action
from smo.web.router import ViewRouter, registerView
import BioReactors

router = ViewRouter('BioReactors', BioReactors)

from .models.SimpleGradostatModel import SimpleGradostatModel, SimpleGradostatDoc 
@registerView(router)
class SimpleGradostatView(ModularPageView):
    label = 'Simple Gradostat'
    modules = [SimpleGradostatModel, SimpleGradostatDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']
    