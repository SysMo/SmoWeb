from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.media.MaterialData import Solids, Fluids
from smo.flow.PipeFlow import PipeFlow

class PipeFlowModel(NumericalModel):
    label = "Pipe Flow"
    figure = ModelFigure(src="ThermoFluids/img/ModuleImages/StraightPipe.svg")
    
    ############# Inputs ###############
    # Fields
    internalDiameter = Quantity('Length', default = (5, 'mm'), label = 'internal diameter (d<sub>i</sub>)')
    externalDiameter = Quantity('Length', default = (6, 'mm'), label = 'external diameter (d<sub>e</sub>)')
    length = Quantity('Length', default = (1, 'm'),    label = 'pipe length (L)')
    surfaceRoughness = Quantity('Length', default = (25, 'um'),    label = 'surface roughness')
    pipeMaterial = ObjectReference(Solids, default = 'StainlessSteel304', label = 'pipe material')
    TWall = Quantity('Temperature', default = (50, 'degC'), label = 'pipe temeprature')
    computeWithIteration = Boolean(default = False, label = 'compute with iteration', 
        description = 'Compute heat flow rate using iteration and logarithmic mean temperature difference (LMTD).\
         If set to False, compuation is performed without iteration, using the difference between the inlet and wall \
         temperatures.')
    maxIterations = Quantity('Dimensionless', default = 20, label = 'max number iterations',
                              maxValue = 100, show='self.computeWithIteration')
    relativeTolerance = Quantity('Dimensionless', default = 0.01, label = 'relative tolerance',
                              show='self.computeWithIteration')        
    pipeInput = FieldGroup([internalDiameter, externalDiameter, length,    pipeMaterial,
        surfaceRoughness, TWall, computeWithIteration, maxIterations, relativeTolerance], label = "Pipe")
    #####
    fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
    inletPressure = Quantity('Pressure', default = (2, 'bar'), label = 'inlet pressure') 
    inletTemperature = Quantity('Temperature', default = (15, 'degC'), label = 'inlet temperature')                    
    inletMassFlowRate = Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'inlet mass flow rate')
    ambientTemperature = Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature')
    flowInput = FieldGroup([fluidName, inletPressure, inletTemperature,    inletMassFlowRate], label = 'Flow')
    #####    
    inputs = SuperGroup([pipeInput, flowInput])
    
    # Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    # Model view
    inputView = ModelView(ioType = "input", superGroups = [inputs], 
        actionBar = inputActionBar, autoFetch = True)
    
    ############# Results ###############
    # Fields
    internalSurfaceArea = Quantity('Area', label = 'internal surface area')
    externalSurfaceArea = Quantity('Area', label = 'external surface area')
    crossSectionalArea = Quantity('Area', label = 'cross sectional area')
    pipeSolidMass = Quantity('Mass', label = 'pipe solid mass')
    pipeOutput = FieldGroup([internalSurfaceArea, externalSurfaceArea,
        crossSectionalArea, pipeSolidMass], label = "Pipe")
    #####
    inletDensity = Quantity('Density', label = 'inlet density')
    fluidVolume = Quantity('Volume', label = 'fluid volume', default = (1, 'L'))
    fluidMass = Quantity('Mass', label = 'fluid mass')
    massFlowRate = Quantity('MassFlowRate', label = 'mass flow rate', default = (1, 'kg/h'))
    volumetricFlowRate = Quantity('VolumetricFlowRate', label = 'volumetric flow rate', default = (1, 'L/h'))
    flowVelocity = Quantity('Velocity', label = 'flow velocity')
    Re = Quantity('Dimensionless', label = 'Reynolds number')
    zeta = Quantity('Dimensionless', label = 'friction factor')
    dragCoefficient = Quantity('Dimensionless', label = 'drag coefficient')
    pressureDrop = Quantity('Pressure', label = 'pressure drop')
    outletPressure = Quantity('Pressure', label = 'outlet pressure')
    outletTemperature  = Quantity('Temperature', label = 'outlet temperature', default = (1, 'degC'))
    flowOutput = FieldGroup([fluidVolume, inletDensity, fluidMass, massFlowRate, volumetricFlowRate, 
        flowVelocity, Re, zeta, dragCoefficient, pressureDrop, outletPressure], label = "Flow")
    #####
    inletEnthalpy = Quantity('SpecificEnthalpy', label = 'inlet enthalpy')
    outletEnthalpy = Quantity('SpecificEnthalpy', label = 'outlet enthalpy')
    cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
    Pr = Quantity('Dimensionless', label = 'Prandtl number')    
    Nu = Quantity('Dimensionless', label = 'Nusselt number')
    alpha = Quantity('HeatTransferCoefficient', label = 'convection coefficient')
    QDot = Quantity('HeatFlowRate', label = 'heat flow rate')
    heatExchangeOutput = FieldGroup([Pr, Nu, alpha, QDot, outletTemperature], label = "Values")    
    #####
    flowResistanceResults = SuperGroup([pipeOutput, flowOutput], label="Flow resistance")
    heatExchangeResults = SuperGroup([heatExchangeOutput], label="Heat exchange")
    
    # Model view
    resultView = ModelView(ioType = "output", superGroups = [flowResistanceResults, heatExchangeResults])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]

    ############# Methods ###############
    def compute(self):
        PipeFlow.compute(self)

class PipeFlowDoc(RestModule):
    name = 'PipeFlowDoc'
    label = 'Pipe Flow (Docs)'