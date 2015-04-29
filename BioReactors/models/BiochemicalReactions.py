'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import smo.model.actions as A 
import smo.dynamical_models.bioreactors.BiochemicalReactions as DM

from smo.model.model import NumericalModel
from smo.web.modules import RestModule

class BiochemicalReactions(NumericalModel):
    label = "Biochemical reactions"
    description = F.ModelDescription("Solver for elementary biochemical reactions", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/BiochemicalReactions.png", show = False)   
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    reactions = F.RecordArray((     
            ('reaction', F.String('E + S -> ES', label = 'Reactions', inputBoxWidth = 200)),           
            ('kForward', F.Quantity('Dimensionless', default = (1.0, '-'), minValue = (0, '-'), label = 'rate constants ->')),
            ('kBackward', F.Quantity('Dimensionless', default = (0.0, '-'), minValue = (0, '-'), label = 'rate constants <-')),
        ),
        toggle = False, 
        label = 'Reactions',
        numRows = 2,
        description = 'Biochemical reactions',
    )
    reactionsFG = F.FieldGroup([reactions], hideContainer = True, label = "Reactions")
    reactionsSG = F.SuperGroup([reactionsFG], label = "Reactions")
    
    variables = F.RecordArray((                
            ('variableName', F.String('E', label = 'Species (variables)')),
            ('initialValue', F.Quantity('Bio_MolarConcentration', default = (1, 'M'), minValue = (0, 'M'), label = 'Initial values')),
        ),
        toggle = False, 
        label = 'variables', 
        numRows = 4,
        description = 'Species of the reactions',
    ) 
    variablesFG = F.FieldGroup([variables], hideContainer = True, label = "Species")
    variablesSG = F.SuperGroup([variablesFG], label = "Species")

    #1.2 Fields - Settings
    tFinal = F.Quantity('Time', default = (0.0, 's'), minValue = (0, 's'), maxValue=(1000, 's'), label = 'simulation time')
    tPrint = F.Quantity('Time', default = (0.0, 's'), minValue = (1e-5, 's'), maxValue = (100, 's'), label = 'print interval')
    solverFG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG], label = 'Settings')
    
    #1.4 Model view
    exampleAction = A.ServerAction("loadEg", label = "Examples", options = (
            ('exampleMMK', 'Michaelis-Menten kinetics'),
            #('exampleMMKI', 'Michaelis-Menten kinetics with inhibition'),
    ))
    
    inputView = F.ModelView(
        ioType = "input", 
        superGroups = [reactionsSG, variablesSG, settingsSG], 
        autoFetch = True,
        actionBar = A.ActionBar([exampleAction]),
    )
    
    #2. ############ Results ###############    
    plot = F.PlotView(
        (
            ('time', F.Quantity('Time', default=(1, 's'))),
            ('E', F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),
        ),
        label = 'Plot'
    )
    
    table = F.TableView(
        (
            ('time', F.Quantity('Time', default=(1, 's'))),
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
        self.exampleMMK()
        
    def exampleMMK(self):
        self.variables[0] = ('E', 4.0)
        self.variables[1] = ('S', 8.0)
        self.variables[2] = ('ES', 0.0)
        self.variables[3] = ('P', 0.0)
        
        self.reactions[0] = ("E + S = ES", 2.0, 1.0)
        self.reactions[1] = ("ES -> E + P", 1.5, 0.0)
        
        self.tFinal = 10.0
        self.tPrint = 0.01
        
    def exampleMMKI(self):
        #:TODO: (MILEN) exampleMMKI 
        #@see http://en.wikipedia.org/wiki/Enzyme_kinetics 
        #     Michaelis-Menten kinetics with intermediate
        #     Multi-substrate reactions
        #     Enzyme inhibition and activation 
        #@see others
        self.variables[0] = ('E', 4.0)
        self.variables[1] = ('S', 8.0)
        self.variables[2] = ('ES', 0.0)
        self.variables[3] = ('P', 0.0)
        
        self.reactions[0] = ("E + S = ES", 2.0, 1.0)
        self.reactions[1] = ("ES <-> E + P", 1.5, 0.5)
        
        self.tFinal = 10.0
        self.tPrint = 0.01
         
    def compute(self):
        # Redefine some fields
        self.redefineFileds()
        
        # Create the model
        model = DM.BiochemicalReactions(self)
         
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
        
    def redefineFileds(self):
        # Create tuples for variables
        varTuples = (('time', F.Quantity('Time', default=(1, 's'))),)
        for var in self.variables:
            X = var[0]
            varTuple = (('%s'%X, F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),)
            varTuples += varTuple
            
        # Redefine Files
        redefinedPlot = F.PlotView(varTuples, 
            label = 'Plot', options = {'ylabel' : 'concentration', 'title' : ''})
        self.redefineField('plot', 'resultsVG', redefinedPlot)
        
        redefinedTable = F.TableView(varTuples,
            label = 'Table', options = {'formats': ['0.000', '0.000', '0.000', '0.000']})
        self.redefineField('table', 'resultsVG', redefinedTable)

class BiochemicalReactionsDoc(RestModule):
    label = 'Biochemical reactions (Doc)'
    
    
