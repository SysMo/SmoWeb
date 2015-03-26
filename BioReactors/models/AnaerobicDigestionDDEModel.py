from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule

from smo.dynamical_models.bioreactors.SimpleChemostat import SimpleChemostat

class AnaerobicDigestionDDEModel(NumericalModel):
    label = "Anaerobic Digestion (DDE)"
    description = ModelDescription("Simulator of an anaerobic digestion model with delay differential equations (DDE)", show = True)
    figure = ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show=False)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    # Parameters
    k1 = Quantity(default = 10.53, minValue = 0, maxValue = 1e6, label = 'k<sub>1</sub>', 
                  description = 'yield coefficient related to substrate-1 consumption from bacteria-1')
    k2 = Quantity(default = 28.6, minValue = 0, maxValue = 1e6, label = 'k<sub>2</sub>', 
                  description = 'yield coefficient related to substrate-2 production from bacteria-1')
    k3 = Quantity(default = 1074., minValue = 0, maxValue = 1e6, label = 'k<sub>3</sub>', 
                  description = 'yield coefficient related to substrate-2 consumption from bacteria-2')
    s1_in = Quantity('Bio_MassConcentration', default = (7.5, 'g/L'), label ='s<sub>1</sub><sup>in</sub>', 
                     description = 'input substrate-1 concentration')
    s2_in = Quantity('Bio_MassConcentration', default = (75., 'g/L'), label ='s<sub>2</sub><sup>in</sub>', 
                     description = 'input substrate-2 concentration')
    a = Quantity('Fraction', default = (0.5, '-'), label ='&#945', 
                 description = 'proportion of organisms that are affected by the dilution rate D')
    D = Quantity('Bio_TimeRate', default = (0.89, '1/day'), minValue = (0, '1/day'), label = 'D',
                 description = 'dilution rate')
    parametersFG = FieldGroup([s1_in, s2_in, k1, k2, k3, a, D], label = 'Parameters')
                        
    # Parameters - specific growth rates
    m1 = Quantity('Bio_TimeRate', default = (1.20, '1/day'), minValue = (0, '1/day'), label = 'm<sub>1</sub>', 
                  description = 'maximum specific growth rate of bacteria-1')
    m2 = Quantity('Bio_TimeRate', default = (0.74, '1/day'), minValue = (0, '1/day'), label = 'm<sub>2</sub>', 
                  description = 'maximum specific growth rate of bacteria-2')
    k_s1 = Quantity('Bio_MassConcentration', default = (7.1, 'g/L'), label = 'k<sub>s1</sub>', 
                    description = 'half saturation constant of bacteria-1')
    k_s2 = Quantity('Bio_MassConcentration', default = (9.28, 'g/L'), label = 'k<sub>s2</sub>', 
                    description = 'half saturation constant of bacteria-2')
    k_I = Quantity('Dimensionless', default = (16., '-'), label = 'k<sub>I</sub>', 
                   description = 'constant in unit: [ sqrt( g/L ) ]')
    parametersMuFG = FieldGroup([m1, m2, k_s1, k_s2, k_I], label = 'Parameters - specific growth rates')
    
    # Parameters - time delays
    tau1 = Quantity('Bio_Time', default = (2., 'day'), minValue = (0, 'day'), label = '&#964<sub>1</sub>',
                    description = 'time delay in conversion of the substrate-1 to viable biomass for bacteria-1')
    tau2 = Quantity('Bio_Time', default = (3., 'day'), minValue = (0, 'day'), label = '&#964<sub>2</sub>',
                    description = 'time delay in conversion of the substrate-2 to viable biomass for bacteria-2')
    parametersTauFG = FieldGroup([tau1, tau2], label = 'Parameters - time delay')
    
    # historical initial conditions
    s1_hist_vals = Quantity('Bio_MassConcentration', default = (3., 'g/L'), label ='s<sub>1</sub><sup>&#91-&#964<sub>1</sub>, 0&#93</sup>', 
                            description = 'historical initial condition for substrate-1 concentration')
    x1_hist_vals = Quantity('Bio_MassConcentration', default = (0.7, 'g/L'), label ='x<sub>1</sub><sup>&#91-&#964<sub>1</sub>, 0&#93</sup>', 
                        description = 'historical initial condition for bacteria-1 concentration')
    s2_hist_vals = Quantity('Bio_MassConcentration', default = (12., 'g/L'), label ='s<sub>2</sub><sup>&#91-&#964<sub>1</sub>, 0&#93</sup>', 
                        description = 'historical initial condition for substrate-2 concentration')
    x2_hist_vals = Quantity('Bio_MassConcentration', default = (0.1, 'g/L'), label ='x<sub>2</sub><sup>&#91-&#964<sub>1</sub>, 0&#93</sup>', 
                    description = 'historical initial condition for bacteria-2 concentration')
    parametersHistFG = FieldGroup([s1_hist_vals, x1_hist_vals, s2_hist_vals, x2_hist_vals], label = 'Historical initial conditions')
        
    inputValuesSG = SuperGroup([parametersMuFG, parametersFG, parametersTauFG, parametersHistFG], label = "Input values")

    #1.2 Fields - Settings
    tFinal = Quantity('Bio_Time', default = (100, 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time')
    tPrint = Quantity('Bio_Time', default = (0.1, 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    solverFG = FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = SuperGroup([solverFG], label = 'Settings')
    
    #1.3 Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    #1.4 Model view
    inputView = ModelView(ioType = "input", superGroups = [inputValuesSG, settingsSG], actionBar = inputActionBar, autoFetch = True)
    
    #2. ############ Results ###############    
    plot = PlotView((
                        ('time', Quantity('Time', default=(1, 'day'))),
                        ('S', Quantity('Density', default=(1, 'g/L'))),
                        ('X', Quantity('Density', default=(1, 'g/L'))),
                        ('D', Quantity('TimeRate', default=(1, '1/day'))),
                    ),
                    label='Plot', 
                    options = {'ylabel' : None})
    table = TableView((
                            ('time', Quantity('Time', default=(1, 'day'))),
                            ('S', Quantity('Density', default=(1, 'g/L'))),
                            ('X', Quantity('Density', default=(1, 'g/L'))),
                            ('D', Quantity('TimeRate', default=(1, '1/day'))),
                        ),
                      label='Table', 
                      options = {'title': 'Title', 'formats': ['0.000', '0.000', '0.000', '0.000']})

    
    resultsVG = ViewGroup([plot, table], label = 'Results')
    resultsSG = SuperGroup([resultsVG])
    
    #2.1 Model view
    resultView = ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    
    def compute(self):
        """
        simpleChemostat = SimpleChemostat(self)
        
        simpleChemostat.prepareSimulation()
        simpleChemostat.run(self)
        
        results = simpleChemostat.getResults()
        self.plot = np.array(results)
        self.table = np.array(results)
        """

class AnaerobicDigestionDDEDoc(RestModule):
    label = 'Anaerobic Digestion (DDE)'
    
    
