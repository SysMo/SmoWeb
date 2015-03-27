from smo.web.view import ModularPageView
from smo.web.router import ViewRouter, registerView
import BioReactors

import models as WM

router = ViewRouter('BioReactors', BioReactors)

@registerView(router)
class ChemostatView(ModularPageView):
    label = 'Chemostat'
    modules = [WM.ChemostatSimpleModel, WM.ChemostatSimpleDoc, WM.ChemostatDDEModel, WM.ChemostatDDEDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']