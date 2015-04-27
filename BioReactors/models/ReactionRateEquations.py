'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import smo.dynamical_models.bioreactors.ReactionRateEquations as DM

from smo.model.model import NumericalModel
from smo.web.modules import RestModule

class ReactionRateEquations(NumericalModel):
    label = "Enzyme kinetic equations"
    description = F.ModelDescription("Solver for enzyme kinetic equations", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show = False) #:TODO: (MILEN) 
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    equations = F.RecordArray((     
            ('equstions', F.String('E + S -> ES', label = 'Equations', inputBoxWidth = 200)),           
            ('kForward', F.Quantity('Dimensionless', default = (1.0, '-'), minValue = (0, '-'), label = 'rate constants -> (forward)')),
            ('kBackward', F.Quantity('Dimensionless', default = (0.0, '-'), minValue = (0, '-'), label = 'rate constants <- (backward)')),
        ),
        toggle = False, 
        label = 'equations',
        numRows = 2,
        description = 'Enzyme kinetic equations',
    )
    equationsFG = F.FieldGroup([equations], hideContainer = True, label = "Enzyme kinetic equations")
    equationsSG = F.SuperGroup([equationsFG], label = "Equations")
    
    variables = F.RecordArray((                
            ('variable', F.String('E', label = 'State variables')),
            ('initValue', F.Quantity('Bio_MolarConcentration', default = (1, 'M'), minValue = (0, 'M'), label = 'Initial values')),
        ),
        toggle = False, 
        label = 'equations', 
        numRows = 4,
        description = 'Variables of the enzyme kinetic equations',
    ) 
    variablesFG = F.FieldGroup([variables], hideContainer = True, label = "Variables")
    variablesSG = F.SuperGroup([variablesFG], label = "Variables")

    #1.2 Fields - Settings
    tFinal = F.Quantity('Bio_Time', default = (20, 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time') #:TODO: (MILEN) time unit: day or s
    tPrint = F.Quantity('Bio_Time', default = (0.1, 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    solverFG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG], label = 'Settings')
    
    #1.4 Model view
    inputView = F.ModelView(ioType = "input", superGroups = [variablesSG, equationsSG, settingsSG], autoFetch = True)
    
    #2. ############ Results ###############    
    plot = F.PlotView(
        (
            ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
            ('E', F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),
        ),
        label = 'Plot'
    )
    
    table = F.TableView(
        (
            ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
            ('E', F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),
        ),
        label = 'Table', 
        options = {'formats': ['0.000', '0.000', '0.000', '0.000']}
    )

    
    resultsVG = F.ViewGroup([plot, table], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG], label = 'Results')
    
    # 2.2 ODEs plot
    odesPlot = F.MPLPlot(label = 'ODEs')
    odesVG = F.ViewGroup([odesPlot], label = 'Ordinary differential equations')
    odesSG = F.SuperGroup([odesVG], label = 'ODEs')
    
    # 2.3 Results plot
    chartPlot = F.MPLPlot(label = 'Chart')
    chartPlotVG = F.ViewGroup([chartPlot], label = 'Chart')
    chartPlotSG = F.SuperGroup([chartPlotVG], label = 'Chart')
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG, odesSG, chartPlotSG], keepDefaultDefs = True)
    
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    def __init__(self):
        self.variables[0] = ('E', 0.1)
        self.variables[1] = ('S', 0.2)
        self.variables[2] = ('ES', 0.0)
        self.variables[3] = ('P', 0.0)
        
        self.equations[0] = ("E + S = ES", 10.1, 1.1)
        self.equations[1] = ("ES -> E + P", 1.1, 0.0)
    
    def redefineFileds(self):
        # Create tuples for variables
        varTuples = (('time', F.Quantity('Bio_Time', default=(1, 'day'))),)
        for var in self.variables:
            X = var[0]
            varTuple = (('%s'%X, F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),)
            varTuples += varTuple
            
        # Redefine Files
        redefinedPlot = F.PlotView(varTuples, 
            label = 'Plot', options = {'ylabel' : 'concentration', 'title' : 'Change in concentrations over time'})
        self.redefineField('plot', 'resultsVG', redefinedPlot)
        
        redefinedTable = F.TableView(varTuples,
            label = 'Table', options = {'formats': ['0.000', '0.000', '0.000', '0.000']})
        self.redefineField('table', 'resultsVG', redefinedTable)
         
    def compute(self):
        # Redefine some fields
        self.redefineFileds()
        
        # Create the model
        model = DM.ReactionRateEquations(self)
         
        # Run simulations 
        model.prepareSimulation()
        model.run(self)
         
        # Show results
        res = model.getResults()
        results = np.array(res)
        self.plot = results
        self.table = results
        
        # Plot results
        model.plotODEsTxt(self.odesPlot)
        model.plotHDFResults(self.chartPlot)

class ReactionRateEquationsDoc(RestModule):
    label = 'Enzyme kinetic equations (Doc)'
    
    
