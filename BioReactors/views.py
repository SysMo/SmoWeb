from smo.web.view import ModularPageView
from smo.web.router import ViewRouter, registerView
import BioReactors

import models as M

router = ViewRouter('BioReactors', BioReactors)

@registerView(router)
class ChemostatView(ModularPageView):
    label = 'Chemostat'
    modules = [M.ChemostatSimple, M.ChemostatSimpleDoc, M.ChemostatDDE, M.ChemostatDDEDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']
    
@registerView(router)
class BiochemicalReactionsView(ModularPageView):
    label = 'Biochemical Reactions'
    modules = [M.BiochemicalReactions, M.BiochemicalReactionsDoc]
    requireJS = ['dygraph', 'dygraphExport']
    requireGoogle = ['visualization']