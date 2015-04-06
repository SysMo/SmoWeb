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
from smo.dynamical_models.tank.TankController import TankController as TC
from smo.media.MaterialData import Fluids
from smo.model.model import NumericalModel
from smo.web.modules import RestModule

#:TODO: rename
#  - FG 'tank' on 'pressure vessel'
#  - 'Tank' on 'CompressGasStorage'


class Tank(NumericalModel):
    label = "Tank"
    description = F.ModelDescription("Tank model with fueling and extraction", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show = False) #:TODO: change the image
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    fluidName = F.Choices(options = Fluids, default = 'ParaHydrogen', 
        label = 'fluid', description = 'fluid of the system')
    fluidAmbientName = F.Choices(options = Fluids, default = 'Air', 
        label = 'ambient fluid', description = 'ambient fluid')
    TAmbient = F.Quantity('Temperature', default = (15.0, 'degC'), 
        label = 'ambient temperature', description = 'ambient temperature')
    globalParams = F.FieldGroup([fluidName, fluidAmbientName, TAmbient], label = "Global")
    
    controller = F.SubModelGroup(FC.TankController, 'FG', label  = 'Controller')
    fuelingSource = F.SubModelGroup(FC.FluidStateSource, 'FG', label = 'Fueling source')
    compressor = F.SubModelGroup(FC.Compressor, 'FG', label = 'Compressor')
    tank = F.SubModelGroup(FC.Tank, 'FG', label = 'Compressed gas storage')
    
    parametersSG = F.SuperGroup([globalParams, fuelingSource, tank, controller, compressor], label = "Parameters")

    #1.2 Fields - Settings
    tFinal = F.Quantity('Time', default = (2000, 's'), minValue = (0, 's'), maxValue=(1.e9, 's'), label = 'simulation time')
    tPrint = F.Quantity('Time', default = (1., 's'), minValue = (1.e-5, 's'), maxValue = (1.e4, 's'), label = 'print interval')
    solverFG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG], label = 'Settings')
    
    #1.3 Actions
    computeAction = A.ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = A.ActionBar([computeAction], save = True)
    
    #1.4 Model view
    inputView = F.ModelView(ioType = "input", superGroups = [parametersSG, settingsSG], actionBar = inputActionBar, autoFetch = True)
    
    #2. ############ Results ###############    
    plot = F.PlotView(
        (
            ('time', F.Quantity('Time', default=(1, 's'))),
            ('pTank', F.Quantity('Pressure', default=(1, 'bar'))),
            ('TTank', F.Quantity('Temperature', default=(1, 'K'))),
        ),
        label='Plot', 
        options = {'ylabel' : None}
    )
    table = F.TableView(
        (
             ('time', F.Quantity('Time', default=(1, 's'))),
             ('pTank', F.Quantity('Pressure', default=(1, 'bar'))),
             ('TTank', F.Quantity('Temperature', default=(1, 'K'))),
        ),
        label='Table', 
        options = {'title': 'Tank fueling-extraction', 'formats': ['0.000', '0.000', '0.000']}
    )
    
    resultsVG = F.ViewGroup([plot, table], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG])
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    
    #================ Methods ================#
    def __init__(self):        
        # Set default values        
        self.controller.initialState = TC.FUELING
        self.controller.tWaitBeforeExtraction = (250., 's')
        self.controller.tWaitBeforeFueling = (50., 's')
        self.controller.pMin = (20., 'bar')
        self.controller.pMax = (300., 'bar')
        self.controller.mDotExtr = (30., 'kg/h')
        self.controller.nCompressor = (1., 'rev/s')
        
        self.fuelingSource.sourceTypeTxt = 'PQ'
        self.fuelingSource.T = (300., 'K')
        self.fuelingSource.p = (1., 'bar')
        self.fuelingSource.q = (0., '-')
        
        self.compressor.etaS = (0.9, '-')
        self.compressor.fQ = (0.1, '-')
        self.compressor.V = (0.25, 'L')
        
        self.tank.wallArea = (2., 'm**2')
        self.tank.volume = (100., 'L')
        self.tank.TInit = (300., 'K')
        self.tank.pInit = (1., 'bar')
        self.tank.linerMaterial = 'StainlessSteel304'
        self.tank.linerMass = (10., 'kg')
        self.tank.linerThickness = (0.05, 'm')
        self.tank.compositeMaterial = 'CarbonFiberComposite'
        self.tank.compositeMass = (15., 'kg')
        self.tank.compositeThickness = (0.1, 'm')
        self.tank.hConvExternal = (100., 'W/m**2-K')
        self.tank.hConvInternalWaiting = (10., 'W/m**2-K')
        self.tank.hConvInternalExtraction = (20., 'W/m**2-K')
        self.tank.hConvInternalFueling = (100., 'W/m**2-K')
        
    def compute(self):
        # Initialize the fluids
        self.fluid = CP.Fluid(self.fluidName)
        self.ambientFluid = CP.Fluid(self.fluidAmbientName)
        
        # Create model object         
        tank = DM.TankModelFactory.create(self)
        
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
    

    