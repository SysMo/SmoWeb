from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.dynamical_models.bioreactors.SimpleChemostat import SimpleChemostat
from collections import OrderedDict

class SimpleChemostatModel(NumericalModel):
    label = "Simple Chemostat"
    description = ModelDescription("Simple chemostat simulator", show = True)
    figure = ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show=False)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    S_in = Quantity('Density', default = (5, 'g/L'), minValue = 0, label ='S<sub>in</sub>', description = 'concentration of the input substrate [mass/volume]')
    m = Quantity('Hertz', default = (3, '1/h'), minValue = 0, label = 'm', description = 'maximal growth rate [1/time]')
    K = Quantity('Density', default = (3.7, 'g/L'), minValue = 0, label = 'K', description = 'half saturation constant [mass/volume]')
    gamma = Quantity(default = 0.6, minValue = 0, maxValue = 1.0, label = '&#947', description = 'yield coefficient of microorganisms [-]')
    D_vals = RecordArray(OrderedDict((
            ('time', Quantity('Time', default = (20, 'h'), minValue = 0, label = 'Duration')),
            ('D', Quantity('Hertz', default = (1, '1/h'), minValue = 0, label = 'D')),
        )), label = 'D', description = 'dilution rate [1/time]')  
    parametersFieldGroup = FieldGroup([S_in, m, K, gamma, D_vals], label = "Parameters")
    
    S0 = Quantity('Density', default = (0, 'g/L'), minValue = 0, label = 'S<sub>0</sub>', description = 'initial concentration of substrate [mass/volume]')
    X0 = Quantity('Density', default = (0.5, 'g/L'), minValue = 0, label = 'X<sub>0</sub>', description = 'initial concentration of microorganisms [mass/volume]')
    initialValuesFieldGroup = FieldGroup([S0, X0], label = "Initial values")
    
    inputValuesSuperGroup = SuperGroup([parametersFieldGroup, initialValuesFieldGroup], label = "Input values")
    
    #1.2 Fields - Settings
    tSimulation = Quantity('Time', default = (100, 'h'), minValue = 0, maxValue=10000, label = 'simulation time')
    tPrint = Quantity('Time', default = (0.1, 'h'), minValue = 1e-4, maxValue=1000, label = 'print interval')
    solverFieldGourp = FieldGroup([tSimulation, tPrint], label = 'Solver')
    
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
                      quantities = ['Time', 'Density', 'Density', 'Hertz'],
                      options = {'title': 'Title', 
                                 'formats': ['0.0000', '0.0000', '0.0000'], 
                                 'columnUnitDefs' : ['h', 'g/L', 'g/L', '1/h']})
    
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
        model.run(tPrint = self.tPrint)
        
        results = model.getResults()
        
        self.plot = np.array(results)
        self.table = np.array(results)

class SimpleChemostatDoc(RestModule):
    label = 'Simple Chemostat (Doc)'
    
    