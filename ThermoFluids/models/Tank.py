'''
Created on April 01, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import smo.model.actions as A
import lib.FluidComponents as FC
import smo.media.CoolProp as CP
import smo.dynamical_models.tank as DM
from smo.model.model import NumericalModel
from smo.web.modules import RestModule
from smo.media.MaterialData import Fluids

class Tank(NumericalModel):
    label = "Tank"
    description = F.ModelDescription("Tank model with refueling and extraction", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show=False) #:TODO: change the image
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    fluidName = F.Choices(options = Fluids, default = 'ParaHydrogen', 
        label = 'fluid', description = 'fluid in the tank')
    @property
    def fluid(self):
        return CP.Fluid(self.fluidName)
    
    TAmbient = F.Quantity('Temperature', default = (15.0, 'degC'), 
        label ='T<sub>amb</sub>', description = 'ambient temperature')
    parametersFG = F.FieldGroup([fluidName, TAmbient], label = "Parameters")
    
    refuelingSource = F.SubModelGroup(FC.FluidStateSource, 'FG', label = 'Refueling source')
    compressor = F.SubModelGroup(FC.Compressor, 'FG', label = 'Compressor')
    
    initialValuesSG = F.SuperGroup([parametersFG, refuelingSource, compressor], label = "Model definitions")
    
    #1.2 Fields - Controller
    controllerSG = F.SubModelGroup(FC.TankController, 'SG', label  = 'Controller')

    #1.2 Fields - Settings
    tFinal = F.Quantity('Time', default = (2000, 's'), minValue = (0, 's'), maxValue=(1.e9, 's'), label = 'simulation time')
    tPrint = F.Quantity('Time', default = (1., 's'), minValue = (1.e-5, 's'), maxValue = (1.e4, 's'), label = 'print interval')
    solverFG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG], label = 'Settings')
    
    #1.3 Actions
    computeAction = A.ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = A.ActionBar([computeAction], save = True)
    
    #1.4 Model view
    inputView = F.ModelView(ioType = "input", superGroups = [initialValuesSG, controllerSG, settingsSG], actionBar = inputActionBar, autoFetch = True)
    
    #2. ############ Results ###############    
    plot = F.PlotView(
        (('time', F.Quantity('Time', default=(1, 's'))),
         ('pTank', F.Quantity('Pressure', default=(1, 'bar'))),
         ('TTank', F.Quantity('Temperature', default=(1, 'K'))),
        ),
        label='Plot', 
        options = {'ylabel' : None}
    )
    table = F.TableView(
        (('time', F.Quantity('Time', default=(1, 's'))),
         ('pTank', F.Quantity('Pressure', default=(1, 'bar'))),
         ('TTank', F.Quantity('Temperature', default=(1, 'K'))),
        ),
        label='Table', 
        options = {'title': 'Tank refueling-extraction cycles', 'formats': ['0.000', '0.000', '0.000']}
    )
    
    resultsVG = F.ViewGroup([plot, table], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG])
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    
    def compute(self):
        # Set the fluid of the components
        self.refuelingSource.fluid = self.fluid
        self.compressor.fluid = self.fluid
        
        # Create objects (TankController and TankModel)         
        self.controller = DM.TankController(self.controllerSG)     
        tank = DM.TankModel(self)
        
        # Run simulation
        tank.prepareSimulation()
        tank.run(self)
        
        # Show the results
        res = tank.getResults()
        results = np.array([res['t'], res['pTank'], res['TTank']]).transpose()
        self.plot = results
        self.table = results
        

class TankDoc(RestModule):
    label = 'Tank (Doc)'
    
    
