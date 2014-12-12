from smo.numerical_model.model import NumericalModel
from smo.numerical_model.fields import *
import numpy as np
from smo.smoflow3d.SimpleMaterials import Fluids
from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict

viewContentObj = ViewContent(np.array([[1,2],[2,3],[3,4]]))

class PlotModel(NumericalModel):
    p = Quantity('Pressure', label = 'pressure')
    g1 = FieldGroup([p], 'FieldGroup')
    
    
    plotView = PlotView(default = viewContentObj, columnLabels = ['p', 'T'], options = {'title': 'TestPlot'})
    tableView = TableView(default = viewContentObj, columnLabels = ['p', 'T'], options = {'title': 'TestTable', 
           'formats': ['0.00E0', '#.00'], 'labels': ['pressure [bar]', 'T sat [K]']})
    tableView2 = TableView(default = viewContentObj, columnLabels = ['p', 'T'], options = {'title': 'nasko table', 
           'formats': ['0.00E0', '#.00'], 'labels': ['pressure \n[bar]', 'T sat [K]']})
    plotViewGroup = ViewGroup([plotView, tableView, tableView2], label="View Group")
    
    plotSuperGroup = SuperGroup([plotViewGroup], label="Plot Super Group" )
    
    otherSuperGroup = SuperGroup([g1], label = "sads")
    
if __name__ == '__main__':
#     FluidPropsCalculator.test()
#     print getFluidConstants()
#     print getLiteratureReferences()
    plotView = PlotModel()