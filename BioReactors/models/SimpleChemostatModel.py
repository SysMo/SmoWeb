from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.dynamical_models.bioreactors.SimpleChemostat import SimpleChemostat
from collections import OrderedDict

class SimpleChemostatModel(NumericalModel):
    label = "Simple Chemostat"
    description = ModelDescription("Simple chemostat simulator", show = True)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    S_in = Quantity(default = 2.2, minValue = 0, label ='conc. of input substrate (S<sub>in</sub>)')
    m = Quantity(default = 3, minValue = 0, label = 'maximal growth rate (m)')
    K = Quantity(default = 3.7, minValue = 0, label = 'half saturation constant (K)')
    gamma = Quantity(default = 0.6, minValue = 0, label = 'yield coefficient (&#947)')
    D_vals = RecordArray(OrderedDict((
            ('D', Quantity(default = 1, minValue = 0, label = 'D')),
            ('days', Quantity(default = 20, minValue = 0, label = 'Time')),
        )), label = 'D_vals')  
    parametersFieldGroup = FieldGroup([S_in, m, K, gamma, D_vals], label = "Parameters")
    
    S0 = Quantity(default = 0, minValue = 0, label = 'S0')
    X0 = Quantity(default = 0.5, minValue = 0, label = 'X0')
    initialValuesFieldGroup = FieldGroup([S0, X0], label = "Initial values")
    
    inputValuesSuperGroup = SuperGroup([parametersFieldGroup, initialValuesFieldGroup], label = "Input values")
    
    #1.2 Fields - Settings
    tSimulation = Quantity(default = 100, minValue = 0, maxValue=10000, label = 'simulation time')
    solverFieldGourp = FieldGroup([tSimulation], label = 'Solver')
    
    settingsSuperGroup = SuperGroup([solverFieldGourp], label = 'Settings')
    
    #1.3 Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    #1.4 Model view
    inputView = ModelView(ioType = "input", superGroups = [inputValuesSuperGroup, settingsSuperGroup], 
        actionBar = inputActionBar, autoFetch = True)
    
    #2. ############ Results ###############
    plot = PlotView(label='Plot', dataLabels = ['time', 'S', 'X', 'D'], options = {'ylabel' : None})
    table = TableView(label='Table', dataLabels = ['time', 'S', 'X', 'D'], 
                      quantities = ['Time', 'Dimensionless', 'Dimensionless', 'Dimensionless'],
                      options = {'title': 'Title', 'formats': ['0.0000', '0.0000', '0.0000']})
    
    resultsViewGroup = ViewGroup([plot, table], label = 'Results')
    results = SuperGroup([resultsViewGroup])
    
    #2.1 Model view
    resultView = ModelView(ioType = "output", superGroups = [results])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    def compute(self):
        model = SimpleChemostat(
            m = self.m,
            K = self.K,
            S_in = self.S_in,
            X_in = 0.0,
            gamma = self.gamma,
            D_vals = self.D_vals,
            S0 = self.S0,
            X0 = self.X0,
            tFinal = self.tSimulation)
        
        model.prepareSimulation()
        model.run(tPrint = 1.0)
        
        results = model.getResults()
        
        self.plot = np.array(results)
        self.table = np.array(results)

class SimpleChemostatDoc(RestModule):
    label = 'Simple Chemostat (Doc)'
    
    