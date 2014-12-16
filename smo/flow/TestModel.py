from smo.model.model import NumericalModel
from smo.model.fields import *
import numpy as np
from smo.media.SimpleMaterials import Fluids
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict

data = np.array([[1,2],[2,3],[3,4]])

class PlotModel(NumericalModel):
    p = Quantity('Pressure', label = 'pressure')
    g1 = FieldGroup([p], 'FieldGroup')
    
    
    plotView = PlotView(default = data, options = {'title': 'TestPlot'})
    tableView = TableView(default = data, dataLabels = ['p', 'T'], options = {'title': 'TestTable', 
           'formats': ['0.00E0', '#.00'], 'labels': ['pressure [bar]', 'T sat [K]']})
    tableView2 = TableView(default = data, dataLabels = ['p', 'T'], options = {'title': 'nasko table', 
           'formats': ['0.00E0', '#.00'], 'labels': ['pressure \n[bar]', 'T sat [K]']})
    plotViewGroup = ViewGroup([plotView, tableView, tableView2], label="View Group")
    
    plotSuperGroup = SuperGroup([plotViewGroup], label="Plot Super Group" )
    
    otherSuperGroup = SuperGroup([g1], label = "sads")
    
if __name__ == '__main__':
#     FluidPropsCalculator.test()
#     print getFluidConstants()
#     print getLiteratureReferences()
    plotView = PlotModel()