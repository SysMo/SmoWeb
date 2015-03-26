from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule

from smo.dynamical_models.bioreactors.ChemostatSimple import ChemostatSimple

class ChemostatSimpleModel(NumericalModel):
    label = "Simple Chemostat"
    description = ModelDescription("Simple chemostat model with ordinary differential equations (ODE)", show = True)
    figure = ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show=False)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    S_in = Quantity('Bio_MassConcentration', default = (5, 'g/L'), minValue = (0, 'g/L'), label ='S<sub>in</sub>', description = 'input substrate concentration')
    X_in = Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), label ='X<sub>in</sub>', description = 'input microorganisms concentration')
    m = Quantity('Bio_TimeRate', default = (3, '1/day'), minValue = (0, '1/day'), label = 'm', description = 'maximum specific growth rate of the microorganisms')
    K = Quantity('Bio_MassConcentration', default = (3.7, 'g/L'), minValue = (0, 'g/L'), label = 'K', description = 'half saturation constant')
    gamma = Quantity(default = 0.6, minValue = 0, maxValue = 1.0, label = '&#947', description = 'yield coefficient of microorganisms')
    D_vals = RecordArray((
                         ('time', Quantity('Bio_Time', default = (20, 'day'), minValue = (0, 'day'), label = 'Duration')),
                         ('D', Quantity('Bio_TimeRate', default = (1, '1/day'), minValue = (0, '1/day'), label = 'D')),
                         ), 
                         label = 'D', description = 'dilution (or washout) rate')  
    parametersFieldGroup = FieldGroup([S_in, X_in, m, K, gamma, D_vals], label = "Parameters")
    
    S0 = Quantity('Bio_MassConcentration', default = (0, 'g/L'), minValue = 0, label = 'S<sub>0</sub>', description = 'initial substrate concentration')
    X0 = Quantity('Bio_MassConcentration', default = (0.5, 'g/L'), minValue = 0, label = 'X<sub>0</sub>', description = 'initial microorganisms concentration')
    initialValuesFieldGroup = FieldGroup([S0, X0], label = "Initial values")
        
    inputValuesSuperGroup = SuperGroup([parametersFieldGroup, initialValuesFieldGroup], label = "Input values")

    #1.2 Fields - Settings
    tFinal = Quantity('Bio_Time', default = (100, 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time')
    tPrint = Quantity('Bio_Time', default = (0.1, 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    solverFieldGourp = FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSuperGroup = SuperGroup([solverFieldGourp], label = 'Settings')
    
    #1.3 Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    #1.4 Model view
    inputView = ModelView(ioType = "input", superGroups = [inputValuesSuperGroup, settingsSuperGroup], actionBar = inputActionBar, autoFetch = True)
    
    #2. ############ Results ###############    
    plot = PlotView((
                        ('time', Quantity('Bio_Time', default=(1, 'day'))),
                        ('S', Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('X', Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('D', Quantity('Bio_TimeRate', default=(1, '1/day'))),
                    ),
                    label='Plot', 
                    options = {'ylabel' : None})
    table = TableView((
                        ('time', Quantity('Bio_Time', default=(1, 'day'))),
                        ('S', Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('X', Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('D', Quantity('Bio_TimeRate', default=(1, '1/day'))),
                      ),
                      label='Table', 
                      options = {'title': 'Simple Chemostat', 'formats': ['0.000', '0.000', '0.000', '0.000']})

    
    resultsVG = ViewGroup([plot, table], label = 'Results')
    resultsSG = SuperGroup([resultsVG])
    
    #2.1 Model view
    resultView = ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    
    def compute(self):
        chemostat = ChemostatSimple(self)
        
        chemostat.prepareSimulation()
        chemostat.run(self)
        
        results = chemostat.getResults()
        self.plot = np.array(results)
        self.table = np.array(results)
        

class ChemostatSimpleDoc(RestModule):
    label = 'Simple Chemostat (Doc)'
    
    
