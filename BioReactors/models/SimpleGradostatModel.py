from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from collections import OrderedDict

class SimpleGradostatModel(NumericalModel):
    label = "Simple Gradostat"
    
    ############# Inputs ###############
    # Fields
    m = Quantity(default = 3, minValue = 0, label = 'm')
    K = Quantity(default = 3.7, minValue = 0, label = 'K')
    S_in = Quantity(default = 2.2, minValue = 0, label ='S_in')
    X_in = Quantity(default = 0, minValue = 0, label = 'X_in')
    gamma = Quantity(default = 1, minValue = 0, label = 'gamma')
    S0 = Quantity(default = 0, minValue = 0, label = 'S0')
    X0 = Quantity(default = 0.5, minValue = 0, label = 'X0')
    
    Arr = RecordArray(OrderedDict((
            ('D', Quantity(default = 1, minValue = 0, label = 'D')),
            ('days', Quantity(default = 1000, minValue = 0, label = 'Days')),
        )), label = 'Arr')
    
    inputsFieldGroup = FieldGroup([m, K, S_in, X_in, gamma, S0, X0, Arr], label = "inputs")
    inputs = SuperGroup([inputsFieldGroup])
    
    # Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    # Model view
    inputView = ModelView(ioType = "input", superGroups = [inputs], 
        actionBar = inputActionBar, autoFetch = True)
    
    ############# Results ###############
    plot = PlotView(label='Plot', dataLabels = ['time', 'S', 'X'])
    table = TableView(label='Table', dataLabels = ['time', 'S', 'X'], 
                      quantities = ['Time', 'Dimensionless', 'Dimensionless'],
                      options = {'title': 'Title', 'formats': ['0.0000', '0.0000']})
    
    resultsViewGroup = ViewGroup([plot, table], label = 'Results')
    results = SuperGroup([resultsViewGroup])
    
    # Model view
    resultView = ModelView(ioType = "output", superGroups = [results])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    def compute(self):
        self.plot = np.array([[1, 0.5, 4], [2, 0.7, 3], [3, 0.5, 5]])
        self.table = np.array([[1, 0.5, 4], [2, 0.7, 3], [3, 0.5, 5]])

class SimpleGradostatDoc(RestModule):
    label = 'Simple Gradostat (Doc)'
    
    