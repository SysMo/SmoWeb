'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
import smo.model.actions as A 
import smo.dynamical_models.bioreactors.BiochemicalReactions as DM

from smo.model.model import NumericalModel
from smo.web.modules import RestModule

class BiochemicalReactions(NumericalModel):
    label = "Biochemical reactions"
    description = F.ModelDescription("Solver for elementary biochemical reactions", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/BiochemicalReactions.png", show = False)
    
    async = True
    progressOptions = {'suffix': 's', 'fractionOutput': True}   
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    reactions = F.RecordArray((     
            ('reactionEquation', F.String('E + S <-> ES', label = 'Equation', inputBoxWidth = 160)),           
            ('rateConstnats', F.String('0.0, 0.0', label = 'Rate constants', inputBoxWidth = 100)),
            ('reactionName', F.String('enzyme binding to a substrate', label = 'Name', inputBoxWidth = 400)),
        ),
        toggle = False, 
        label = 'Reactions',
        numRows = 2,
        description = 'Biochemical reactions',
    )
    reactionsFG = F.FieldGroup([reactions], hideContainer = True, label = "Reactions")
    reactionsSG = F.SuperGroup([reactionsFG], label = "Reactions")
    
    species = F.RecordArray((                
            ('speciesVariable', F.String('E', label = 'Variable', inputBoxWidth = 70)),
            ('initialValue', F.Quantity('Bio_MolarConcentration', default = (1, 'M'), minValue = (0, 'M'), 
                label = 'Initial value', inputBoxWidth = 75)
            ),
            ('speciesName', F.String('enzyme', label = 'Name', inputBoxWidth = 270)),
        ),
        toggle = False, 
        label = 'species', 
        numRows = 4,
        description = 'Species of the reactions',
    ) 
    speciesFG = F.FieldGroup([species], hideContainer = True, label = "Species")
    speciesSG = F.SuperGroup([speciesFG], label = "Species")

    #1.2 Fields - Settings
    tFinal = F.Quantity('Time', default = (0.0, 's'), minValue = (0, 's'), maxValue=(1000, 's'), label = 'simulation time')
    tPrint = F.Quantity('Time', default = (0.0, 's'), minValue = (1e-3, 's'), maxValue = (100, 's'), label = 'print interval')
    solverFG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG], label = 'Settings')
    
    #1.4 Model view
    exampleAction = A.ServerAction("loadEg", label = "Examples", options = (
        ('exampleMMK', 'Michaelis-Menten kinetics'),
        #('exampleMMKI', 'Michaelis-Menten kinetics with inhibition'),
    ))
    
    inputView = F.ModelView(
        ioType = "input", 
        superGroups = [reactionsSG, speciesSG, settingsSG], 
        autoFetch = True,
        actionBar = A.ActionBar([exampleAction]),
    )
    
    #2. ############ Results ###############
    storage = F.HdfStorage(hdfFile = 'BioReactors_SimulationResults.h5', hdfGroup = '/BiochemicalReactions')
    
    dataSeries = (
        ('time', F.Quantity('Time', default=(1, 's'))),
        ('E', F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),
    )
    
    plot = F.PlotView(
        dataSeries,
        label = 'Plot',
        useHdfStorage = True,
        storage = 'storage'
    )
    
    table = F.TableView(
        dataSeries,
        label = 'Table', 
        options = {'formats': ['0.000', '0.000', '0.000', '0.000']},
        useHdfStorage = True,
        storage = 'storage'
    )

    storageVG = F.ViewGroup([storage], show="false")
    resultsVG = F.ViewGroup([plot, table], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG, storageVG], label = 'Results')
    
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
        self.species[0] = ('E', 4.0, 'enzyme')
        self.species[1] = ('S', 8.0, 'substrate')
        self.species[2] = ('ES', 0.0, 'complex')
        self.species[3] = ('P', 0.0, 'product')
        
        self.reactions[0] = ('E + S = ES', '2.0, 1.0', 'an enzyme binding to a substrate form a complex (reversible process)')
        self.reactions[1] = ('ES -> E + P', '1.5', 'a complex decomposition to a product and the enzyme')
        
        self.tFinal = 10.0
        self.tPrint = 0.01
        
    def exampleMMKI(self):
        #:TODO: (MILEN) exampleMMKI 
        #@see http://en.wikipedia.org/wiki/Enzyme_kinetics 
        #     Michaelis-Menten kinetics with intermediate
        #     Multi-substrate reactions
        #     Enzyme inhibition and activation 
        #@see others
        self.species.resize(3)
        self.species[0] = ('E', 4.0, 'enzyme')
        self.species[1] = ('S', 8.0, 'substrate')
        self.species[2] = ('ES', 0.0, 'complex')
        
        self.reactions.resize(1)
        self.reactions[0] = ('E + S = ES', '2.0, 1.0', 'an enzyme binding to a substrate form a complex (reversible process)')
        
        self.tFinal = 10.0
        self.tPrint = 0.01
         
    def computeAsync(self):
        # Redefine some fields
        self.redefineFileds()
        
        # Create the model
        model = DM.BiochemicalReactions(self)
         
        # Tun simulation
        model.prepareSimulation()
        model.run(self)
         
        # Show results
        self.storage = model.resultStorage.simulationName
        
        # Plot results
        model.plotODEsTxt(self.odesPlot)
        model.plotHDFResults(self.chartPlot)
        
    def redefineFileds(self):
        # Create tuples for species
        speciesTuples = (('time', F.Quantity('Time', default=(1, 's'))),)
        datasetColumns = ['t']
        for itSpecies in self.species:
            X = itSpecies[0] #species variable
            speciesTuple = (('%s'%X, F.Quantity('Bio_MolarConcentration', default=(1, 'M'))),)
            speciesTuples += speciesTuple
            datasetColumns.append('%s'%X)
            
        # Redefine Fields
        redefinedStorage = F.HdfStorage(
            hdfFile = 'BioReactors_SimulationResults.h5',
            hdfGroup = '/BiochemicalReactions', datasetColumns=datasetColumns)
        self.redefineField('storage', 'storageVG', redefinedStorage)
        
        redefinedPlot = F.PlotView(speciesTuples, 
            label = 'Plot', options = {'ylabel' : 'concentration', 'title' : ''}, 
            useHdfStorage = True, storage = 'storage')
        self.redefineField('plot', 'resultsVG', redefinedPlot)
        
        redefinedTable = F.TableView(speciesTuples,
            label = 'Table', options = {'formats': ['0.000', '0.000', '0.000', '0.000']}, 
            useHdfStorage = True, storage = 'storage')
        self.redefineField('table', 'resultsVG', redefinedTable)

class BiochemicalReactionsDoc(RestModule):
    label = 'Biochemical reactions (Doc)'
    