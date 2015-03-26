from smo.web.view import ModularPageView
from smo.web.view import action
from smo.web.router import ViewRouter, registerView
import BioReactors

router = ViewRouter('BioReactors', BioReactors)

from .models import ChemostatDDEModel, ChemostatDDEDoc, ChemostatSimpleModel, ChemostatSimpleDoc
@registerView(router)
class ChemostatView(ModularPageView):
    label = 'Chemostat'
    modules = [ChemostatSimpleModel, ChemostatSimpleDoc, ChemostatDDEModel, ChemostatDDEDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']