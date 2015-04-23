'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import smo.dynamical_models.bioreactors.ChemostatSimple as DM

from smo.model.model import NumericalModel
from smo.web.modules import RestModule

class ChemostatSimple(NumericalModel):
    label = "Simple Chemostat"
    description = F.ModelDescription("Simple chemostat model with ordinary differential equations (ODE)", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show=False)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    S_in = F.Quantity('Bio_MassConcentration', default = (5, 'g/L'), minValue = (0, 'g/L'), label ='S<sub>in</sub>', description = 'input substrate concentration')
    X_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), label ='X<sub>in</sub>', description = 'input microorganisms concentration')
    m = F.Quantity('Bio_TimeRate', default = (3, '1/day'), minValue = (0, '1/day'), label = 'm', description = 'maximum specific growth rate of the microorganisms')
    K = F.Quantity('Bio_MassConcentration', default = (3.7, 'g/L'), minValue = (0, 'g/L'), label = 'K', description = 'half saturation constant')
    gamma = F.Quantity(default = 0.6, minValue = 0, maxValue = 1.0, label = '&#947', description = 'yield coefficient of microorganisms')
    D_vals = F.RecordArray((
                         ('time', F.Quantity('Bio_Time', default = (20, 'day'), minValue = (0, 'day'), label = 'Duration')),
                         ('D', F.Quantity('Bio_TimeRate', default = (1, '1/day'), minValue = (0, '1/day'), label = 'D')),
                         ), 
                         label = 'D', description = 'dilution (or washout) rate')  
    parametersFieldGroup = F.FieldGroup([S_in, X_in, m, K, gamma, D_vals], label = "Parameters")
    
    S0 = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), minValue = 0, label = 'S<sub>0</sub>', description = 'initial substrate concentration')
    X0 = F.Quantity('Bio_MassConcentration', default = (0.5, 'g/L'), minValue = 0, label = 'X<sub>0</sub>', description = 'initial microorganisms concentration')
    initialValuesFieldGroup = F.FieldGroup([S0, X0], label = "Initial values")
        
    inputValuesSuperGroup = F.SuperGroup([parametersFieldGroup, initialValuesFieldGroup], label = "Input values")

    #1.2 Fields - Settings
    tFinal = F.Quantity('Bio_Time', default = (100, 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time')
    tPrint = F.Quantity('Bio_Time', default = (0.1, 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    solverFieldGourp = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSuperGroup = F.SuperGroup([solverFieldGourp], label = 'Settings')
    
    #1.4 Model view
    inputView = F.ModelView(ioType = "input", superGroups = [inputValuesSuperGroup, settingsSuperGroup], autoFetch = True)
    
    #2. ############ Results ###############    
    plot = F.PlotView((
                        ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
                        ('S', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('X', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('D', F.Quantity('Bio_TimeRate', default=(1, '1/day'))),
                    ),
                    label='Plot', 
                    options = {'ylabel' : None})
    table = F.TableView((
                        ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
                        ('S', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('X', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
                        ('D', F.Quantity('Bio_TimeRate', default=(1, '1/day'))),
                      ),
                      label='Table', 
                      options = {'title': 'Simple Chemostat', 'formats': ['0.000', '0.000', '0.000', '0.000']})

    
    resultsVG = F.ViewGroup([plot, table], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG])
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    
    def compute(self):
        chemostat = DM.ChemostatSimple(self)
        
        chemostat.prepareSimulation()
        chemostat.run(self)
        
        res = chemostat.getResults()
        print res
        results = np.array(res)
        print results
        self.plot = results
        self.table = results
        

class ChemostatSimpleDoc(RestModule):
    label = 'Simple Chemostat (Doc)'
    
    
