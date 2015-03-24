from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.media.MaterialData import Solids, Fluids
from smo.flow import FrictionFlow
from smo.media.CoolProp.CoolProp import FluidState
import math
import numpy as np

# TOutRec = []

class PipeFlow(NumericalModel):
    label = "Pipe Flow"
    figure = ModelFigure(src="ThermoFluids/img/ModuleImages/StraightPipe.svg")
    description = ModelDescription("Pipe flow calculator accounting for heat exchange and pressure drop", show = True)

    ############# Inputs ###############
    # Fields
    internalDiameter = Quantity('Length', default = (5, 'mm'), label = 'internal diameter (d<sub>i</sub>)')
    externalDiameter = Quantity('Length', default = (6, 'mm'), label = 'external diameter (d<sub>e</sub>)')
    length = Quantity('Length', default = (1, 'm'),    label = 'pipe length (L)')
    surfaceRoughness = Quantity('Length', default = (25, 'um'),    label = 'surface roughness')
    pipeMaterial = ObjectReference(Solids, default = 'StainlessSteel304', label = 'pipe material')
    TWall = Quantity('Temperature', default = (50, 'degC'), label = 'pipe temeprature')
    computationWithIteration = Boolean(default = False, label = 'compute with iteration', 
        description = 'Compute heat flow rate using iteration and logarithmic mean temperature difference (LMTD).\
         If set to False, compuation is performed without iteration, using the difference between the inlet and wall \
         temperatures.')
    maxIterations = Quantity('Dimensionless', default = 20, label = 'max number iterations',
                              maxValue = 100, show='self.computationWithIteration')
    relativeTolerance = Quantity('Dimensionless', default = 0.01, label = 'relative tolerance',
                              show='self.computationWithIteration')        
    pipeInput = FieldGroup([internalDiameter, externalDiameter, length, pipeMaterial,
        surfaceRoughness, TWall, computationWithIteration, maxIterations, relativeTolerance], label = "Pipe")
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
        if (self.computationWithIteration == True):
            self.computeWithIteration()
        else: 
            self.computeWithoutIteration()    
    
    def computeWithoutIteration(self):
        self.computeGeometry()
        self.computePressureDrop()
        self.computeHeatExchange()
    
    def computeWithIteration(self):
        self.computeGeometry()
        
        #In state
        fStateIn = FluidState(self.fluidName)
        fStateIn.update_Tp(self.inletTemperature, self.inletPressure)
        self.inletEnthalpy = fStateIn.h
        
        # Mean state
        fStateMean = FluidState(self.fluidName)
        outletTemperature_guess = (self.inletTemperature + self.TWall) / 2.
        self.outletTemperature = outletTemperature_guess
        prevOutletTemperature = self.outletTemperature
        
        for i in range(int(self.maxIterations)):
            meanTemperature = (self.inletTemperature + outletTemperature_guess) / 2.
            fStateMean.update_Tp(meanTemperature, self.inletPressure)
            self.computePressureDrop(fStateFilm = fStateMean)
            self.computeHeatExchange(fStateFilm = fStateMean)
            if (abs(prevOutletTemperature - self.outletTemperature) / prevOutletTemperature < self.relativeTolerance):
                break
            if (abs(self.outletTemperature - self.TWall) < 0.01):
                break
            outletTemperature_guess = self.outletTemperature
        
#         T = np.array(TOutRec)
#         plt.plot(T)
#         plt.plot(np.arange(len(T)), self.TWall * np.ones(len(T)))
#         plt.show()
        
    def computeGeometry(self):
        if (self.externalDiameter <= self.internalDiameter):
            raise ValueError('External diameter value must be bigger than internal diameter value.')
        self.crossSectionalArea = np.pi / 4 * self.internalDiameter ** 2
        self.fluidVolume = self.crossSectionalArea * self.length
        self.internalSurfaceArea = np.pi * self.internalDiameter * self.length
        self.externalSurfaceArea = np.pi * self.externalDiameter * self.length
        print self.pipeMaterial
        self.pipeSolidMass = self.pipeMaterial['refValues']['density'] \
            * np.pi / 4 * (self.externalDiameter**2 - self.internalDiameter**2) * self.length
        
    def computePressureDrop(self, fStateFilm = None):
        
        if (fStateFilm is None):
            fStateFilm = FluidState(self.fluidName)
            fStateFilm.update_Tp(self.inletTemperature, self.inletPressure)
        
        self.inletDensity = fStateFilm.rho
        self.massFlowRate = self.inletMassFlowRate
        self.fluidMass = self.fluidVolume * self.inletDensity
        self.volumetricFlowRate = self.massFlowRate / self.inletDensity    
        self.flowVelocity = self.massFlowRate / (self.inletDensity * self.crossSectionalArea)
        self.Re = self.inletDensity * self.flowVelocity * self.internalDiameter / fStateFilm.mu
        self.zeta = FrictionFlow.ChurchilCorrelation(self.Re, self.internalDiameter, self.surfaceRoughness)
        self.dragCoefficient = self.zeta * self.length / self.internalDiameter
        self.pressureDrop = self.dragCoefficient * self.inletDensity * self.flowVelocity * self.flowVelocity / 2.
        self.outletPressure = self.inletPressure - self.pressureDrop
        if (self.outletPressure <= 0):
            raise ValueError("This mass flow rate cannot be achieved.")    
    
    
    # Heat Atlas, p.697, eq. 26, 27    
    def computeHeatExchange(self, fStateFilm = None):      
        if (fStateFilm is None):
            fStateFilm = FluidState(self.fluidName)
            fStateFilm.update_Tp(self.inletTemperature, self.inletPressure)
            self.inletEnthalpy = fStateFilm.h
        
        ####
#         self.inletDensity = fStateFilm.rho
#         self.flowVelocity = self.massFlowRate / (self.inletDensity * self.crossSectionalArea)
#         self.Re = self.inletDensity * self.flowVelocity * self.internalDiameter / fStateFilm.mu
        ###
        
        self.Pr = fStateFilm.Pr
        self.cond = fStateFilm.cond
        
        # Determining Nusselt number
        if (self.Re <= 2.3e3):
            # laminar flow
            self.Nu = 3.66
        elif (self.Re > 2.3e3 and self.Re < 1e4):
            # transition    
            interpCoeff = (self.Re - 2.3e3) / (1e4 - 2.3e3) 
            Nu_low = 3.66
            xi = (1.8 * 4 - 1.5)**(-2)
            Nu_high = ((xi / 8.) * 1e4 * self.Pr) / (1 + 12.7 * math.sqrt(xi / 8.) * (self.Pr**(2 / 3.) - 1)) * \
            (1 + (self.internalDiameter / self.length)**(2 / 3.))
            self.Nu = interpCoeff * Nu_high + (1 - interpCoeff) * Nu_low
        elif (self.Re >= 1e4 and self.Re <= 1e6):
            # turbulent flow
            xi = (1.8 * math.log(self.Re, 10) - 1.5)**(-2)
            self.Nu = ((xi / 8.) * self.Re * self.Pr) / (1 + 12.7 * math.sqrt(xi / 8.) * (self.Pr**(2 / 3.) - 1))
        elif (self.Re > 1e6):
            raise ValueError("Outside range of validity")
        
        self.alpha = self.cond * self.Nu / self.internalDiameter
        
        if (self.computationWithIteration == True):            
            LMTD = - (self.outletTemperature - self.inletTemperature) / \
                    math.log((self.TWall - self.inletTemperature) / \
                        (self.TWall - self.outletTemperature))
            self.QDot = self.alpha * self.internalSurfaceArea * LMTD
        else:
            self.QDot = self.alpha * self.internalSurfaceArea * (self.inletTemperature - self.TWall)
        
        self.outletEnthalpy = self.inletEnthalpy - (self.QDot / self.massFlowRate)
        
        fStateOut = FluidState(self.fluidName)
        fStateOut.update_ph(self.outletPressure, self.outletEnthalpy)
        prevOutletTemperature = self.outletTemperature 
        self.outletTemperature = fStateOut.T
        
        if ((self.outletTemperature - self.TWall)*(self.inletTemperature - self.TWall) < 0):
            if (self.computationWithIteration == True):
                self.outletTemperature = 0.5 * prevOutletTemperature + 0.5 * self.TWall
            else:
                self.outletTemperature = self.TWall
        else:
            if (self.computationWithIteration == True):
                self.outletTemperature = 0.9 * prevOutletTemperature + 0.1 * self.outletTemperature    
            
#         TOutRec.append(self.outletTemperature)
#         print ('-------')
#         print ('inletTemperature: %e'%self.inletTemperature)
#         print ('outletTemperature: %e'%self.outletTemperature)
#         print ('TWall: %e'%self.TWall)
#         print ('dTOut = %e'%(self.outletTemperature - self.TWall))
#         print ('')
        


# Left for testing purposes !!!    
#     @staticmethod
#     def computeWithIteration1(self):
#         ### Geometry
#         if (self.externalDiameter <= self.internalDiameter):
#             raise ValueError('External diameter value must be bigger than internal diameter value.')
#         self.crossSectionalArea = np.pi / 4 * self.internalDiameter ** 2
#         self.fluidVolume = self.crossSectionalArea * self.length
#         self.internalSurfaceArea = np.pi * self.internalDiameter * self.length
#         self.externalSurfaceArea = np.pi * self.externalDiameter * self.length
#         self.pipeSolidMass = self.pipeMaterial['refValues']['density'] \
#             * np.pi / 4 * (self.externalDiameter**2 - self.internalDiameter**2) * self.length
#         
#         ### Flow
#         self.massFlowRate = self.inletMassFlowRate
#         outletTemperature_guess = (self.inletTemperature + self.TWall) / 2.
#         fStateIn = FluidState(self.fluidName)
#         fStateMean = FluidState(self.fluidName)
#         fStateOut = FluidState(self.fluidName)
#         fStateIn.update_Tp(self.inletTemperature, self.inletPressure)
#         self.inletEnthalpy = fStateIn.h
#         
#         for i in range(10):
#             meanTemperature = (self.inletTemperature + outletTemperature_guess) / 2.        
#             ### Flow
#             fStateMean.update_Tp(meanTemperature, self.inletPressure)
#             self.inletDensity = fStateMean.rho
#             self.fluidMass = self.fluidVolume * self.inletDensity
#             self.volumetricFlowRate = self.massFlowRate / self.inletDensity    
#             self.flowVelocity = self.massFlowRate / (self.inletDensity * self.crossSectionalArea )
#             self.Re = self.inletDensity * self.flowVelocity * self.internalDiameter / fStateMean.mu
#             
#             ### Pressure drop
#             self.zeta = FrictionFlow.ChurchilCorrelation(self.Re, self.internalDiameter, self.surfaceRoughness)
#             self.dragCoefficient = self.zeta * self.length / self.internalDiameter
#             self.pressureDrop = self.dragCoefficient * self.inletDensity * self.flowVelocity * self.flowVelocity / 2
#             self.outletPressure = self.inletPressure - self.pressureDrop
#             
#             ### Heat exchange
#             self.Pr = fStateMean.Pr
#             self.cond = fStateMean.cond
#             
#             # Determining Nusselt number
#             if (self.Re <= 2.3e3):
#                 # laminar flow
#                 self.Nu = 3.66
#             elif (self.Re > 2.3e3 and self.Re < 1e4):
#                 # transition    
#                 interpCoeff = (self.Re - 2.3e3) / (1e4 - 2.3e3) 
#                 Nu_low = 3.66
#                 eps = (1.8 * 4 - 1.5)**(-2)
#                 Nu_high = ((eps / 8.) * 1e4 * self.Pr) / (1 + 12.7 * math.sqrt(eps / 8.) * (self.Pr**(2 / 3.) - 1)) * \
#                 (1 + (self.internalDiameter / self.length)**(2 / 3.))
#                 self.Nu = interpCoeff * Nu_high + (1 - interpCoeff) * Nu_low
#             elif (self.Re >= 1e4 and self.Re <= 1e6):
#                 # turbulent flow
#                 eps = (1.8 * math.log10(self.Re) - 1.5)**(-2)
#                 self.Nu = ((eps / 8.) * self.Re * self.Pr) / (1 + 12.7 * math.sqrt(eps / 8.) * (self.Pr**(2 / 3.) - 1)) * \
#                 (1 + (self.internalDiameter / self.length)**(2 / 3.))
#             elif (self.Re > 1e6):
#                 raise ValueError("Outside range of validity")
#             
#             self.alpha = self.cond * self.Nu / self.internalDiameter
#             LMTD = - (outletTemperature_guess - self.inletTemperature) / \
#                     math.log((self.TWall - self.inletTemperature) / \
#                         (self.TWall - outletTemperature_guess))
#             #self.QDot = self.alpha * self.internalSurfaceArea * (meanTemperature - self.TWall)
#             self.QDot = self.alpha * self.internalSurfaceArea * LMTD
#             self.outletEnthalpy = self.inletEnthalpy - (self.QDot / self.massFlowRate)
#             fStateOut.update_ph(self.outletPressure, self.outletEnthalpy)
#             outletTemperature_guess = fStateOut.T    
#         self.outletTemperature = outletTemperature_guess

class PipeFlowDoc(RestModule):
    name = 'PipeFlowDoc'
    label = 'Pipe Flow (Doc)'
