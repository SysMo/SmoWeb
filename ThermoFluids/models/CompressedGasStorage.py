'''
Created on April 01, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import lib.CompressedGasStorageComponents as GSC
import smo.media.CoolProp as CP
import smo.dynamical_models.tank as DM
from smo.dynamical_models.tank.TankController import TankController as TC
from smo.media.MaterialData import Fluids
from smo.model.model import NumericalModel
from smo.web.modules import RestModule

class CompressedGasStorage(NumericalModel):
    label = "Compressed Gas Storage"
    description = F.ModelDescription("Compressed gas storage model with fueling and extraction", show = True)
    figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/CompressedGasStorage.svg")
    
    async = True
    progressOptions = {'total': 1., 'suffix': '%', 'fractionOutput': False}
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    fluidName = F.Choices(options = Fluids, default = 'ParaHydrogen', 
        label = 'fluid', description = 'fluid of the system')
    fluidAmbientName = F.Choices(options = Fluids, default = 'Air', 
        label = 'ambient fluid', description = 'ambient fluid')
    TAmbient = F.Quantity('Temperature', default = (15.0, 'degC'), 
        label = 'ambient temperature', description = 'ambient temperature')
    globalParams = F.FieldGroup([fluidName, TAmbient], label = "Global")
    
    controller = F.SubModelGroup(GSC.Controller, 'SG', label  = 'Controller')
    fuelingSource = F.SubModelGroup(GSC.FluidStateSource, 'FG', label = 'Fueling source')
    compressor = F.SubModelGroup(GSC.Compressor, 'FG', label = 'Compressor')
    cooler = F.SubModelGroup(GSC.Cooler, 'FG', label = 'Cooler')
    tank = F.SubModelGroup(GSC.Tank, 'SG', label = 'Pressure vessel')
    
    parametersSG = F.SuperGroup([globalParams, fuelingSource, compressor, cooler], label = "Parameters")

    #1.2 Fields - Settings
    tFinal = F.Quantity('Time', default = (2500, 's'), minValue = (0, 's'), maxValue=(1.e9, 's'), label = 'simulation time')
    tPrint = F.Quantity('Time', default = (1., 's'), minValue = (1.e-5, 's'), maxValue = (1.e4, 's'), label = 'print interval')
    solverFG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG], label = 'Settings')
    
    #1.4 Model view
    inputView = F.ModelView(ioType = "input", superGroups = [parametersSG, tank, controller, settingsSG], autoFetch = True)
    
    #2. ############ Results ###############
    #2.1 Tank results
    tankRes = F.SubModelGroup(GSC.TankRes, 'FG', label = 'Masses')
    tankResSG = F.SuperGroup([tankRes], label = 'Vessel')
    
    #2.2 Plots
    resultColumns = (
        ('time', F.Quantity('Time', default = (1, 's'))),
        ('vessel pressure', F.Quantity('Pressure', default = (1, 'bar'))),
        ('vessel density', F.Quantity('Density', default = (1, 'kg/m**3'))),
        ('mass', F.Quantity('Mass', default = (1, 'kg'))),
        ('vessel temperature', F.Quantity('Temperature', default = (1, 'degC'))),
        ('liner temperature', F.Quantity('Temperature', default = (1, 'degC'))),
        ('composite surface temperature', F.Quantity('Temperature', default = (1, 'degC'))),
        ('compressor outlet temperature', F.Quantity('Temperature', default = (1, 'degC'))),
        ('cooler outlet temperature', F.Quantity('Temperature', default = (1, 'degC'))),
        ('cooler heat flow', F.Quantity('HeatFlowRate', default = (1, 'kW'))),
        ('vessel heat flow', F.Quantity('HeatFlowRate', default = (1, 'W'))),
        ('fueling flow rate', F.Quantity('MassFlowRate', default = (1, 'kg/h'))),
        ('integrated compressor work', F.Quantity('Energy', default = (1, 'kWh'))),
    )
    
    plotTank = F.PlotView(
        resultColumns,
        label = 'Vessel state', 
        options = {'ylabel' : None},
        visibleColumns = [0, 1, 4, 5, 6],
    )
    
    plotTankFluidMass = F.PlotView(
        resultColumns,
        label = 'Fill mass', 
        options = {'ylabel' : None},
        visibleColumns = [0, 3],
    )
    
    plotFueling = F.PlotView(
        resultColumns,
        label = 'Fueling', 
        options = {'ylabel' : None},
        visibleColumns = [0, 4, 8, 11],
    )
    
    plotQDot = F.PlotView(
        resultColumns,
        label = 'Heat flow rates', 
        options = {'ylabel' : None},
        visibleColumns = [0, 9, 10],
    )
    
    plotCompressor = F.PlotView(
        resultColumns,
        label = 'Compressor', 
        options = {'ylabel' : None},
        visibleColumns = [0, 12],
    )
    
    plotsVG = F.ViewGroup([plotTank, plotTankFluidMass, plotFueling, plotQDot, plotCompressor], label = 'Results')
    plotsSG = F.SuperGroup([plotsVG], label = 'Plots')
    
    #2.3 Table 
    table = F.TableView(
        resultColumns,
        label = 'Table', 
        options = {'title': 'Compressed gas storage fueling-extraction', 'formats': ['0.00']},
    )
    tableVG = F.ViewGroup([table], label = 'Results')
    tableSG = F.SuperGroup([tableVG], label = 'Table')
    
    #2.4 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [plotsSG, tableSG, tankResSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    #================ Methods ================#
    def __init__(self):        
        # Set default values        
        self.controller.initialState = TC.FUELING
        self.controller.tWaitBeforeExtraction = (500., 's')
        self.controller.tWaitBeforeFueling = (0., 's')
        self.controller.pMin = (2., 'bar')
        self.controller.pMax = (100., 'bar')
        self.controller.mDotExtr = (10., 'kg/h')
        self.controller.nCompressor = (30., 'rev/s')
        
        self.fuelingSource.sourceTypeTxt = 'TP'
        self.fuelingSource.T = (15., 'degC')
        self.fuelingSource.p = (1., 'bar')
        self.fuelingSource.q = (0., '-')
        
        self.compressor.etaS = (0.8, '-')
        self.compressor.fQ = (0.2, '-')
        self.compressor.V = (1., 'L')
        
        self.cooler.workingState = 1
        self.cooler.epsilon = 1.
        self.cooler.TCooler = (-10, 'degC')
        
        self.tank.wallArea = (2., 'm**2')
        self.tank.volume = (100., 'L')
        self.tank.TInit = (15., 'degC')
        self.tank.pInit = (1., 'bar')
        self.tank.linerMaterial = 'Aluminium6061'
        self.tank.linerThickness = (0.005, 'm')
        self.tank.compositeMaterial = 'CarbonFiberComposite'
        self.tank.compositeThickness = (0.01, 'm')
        self.tank.hConvExternal = (10., 'W/m**2-K')
        self.tank.hConvInternalWaiting = (50., 'W/m**2-K')
        self.tank.hConvInternalExtraction = (100., 'W/m**2-K')
        self.tank.hConvInternalFueling = (500., 'W/m**2-K')
              
    def computeAsync(self):
        #self.updateProgress = lambda x : x
        
        # Initialize the fluids
        self.fluid = CP.Fluid(self.fluidName)
        self.ambientFluid = CP.Fluid(self.fluidAmbientName)
        
        # Create model object         
        tankModel = DM.TankModelFactory.create(self)
        
        # Run simulation
        tankModel.prepareSimulation()
        tankModel.run(self)
        
        # Show results
        self.showResults(tankModel)
        
    def showResults(self, tankModel):
        # Show some results
        self.tankRes.linerMass = tankModel.liner.mass
        self.tankRes.compositeMass = tankModel.composite.mass
        
        # Show plots and table
        res = tankModel.getResults()
        results = np.array([
            res['t'], 
            res['pTank'], 
            res['rhoTank'],
            res['mTank'],
            res['TTank'], 
            res['TLiner_2'], 
            res['TComp_4'],
            res['TCompressorOut'],
            res['TCoolerOut'],
            res['QDotCooler'],
            res['QDotComp'],
            res['mDotFueling'],
            res['WRealCompressor']
        ])
        results = results.transpose()
        
        self.plotTank = results
        self.plotTankFluidMass = results
        self.plotFueling = results
        self.plotQDot = results
        self.plotCompressor = results
        self.table = results

class CompressedGasStorageDoc(RestModule):
    label = 'Compressed Gas Storage (Doc)'
