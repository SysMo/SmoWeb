'''
Created on Mar 31, 2015

@author:  Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
from collections import OrderedDict
from smo.model.model import NumericalModel
import smo.dynamical_models.thermofluids as DM
from smo.dynamical_models.tank.TankController import TankController as TC
from smo.media.MaterialData import Solids

portType = OrderedDict((
    ('R', 'R'),
    ('C', 'C'),
))

class EmptyModel(NumericalModel):
    FG = F.FieldGroup([], label = '')
    modelBlocks = []

class TankController(NumericalModel):
    initialState = F.Choices(
        OrderedDict((
            (TC.REFUELING, 'refueling'),
            (TC.EXTRACTION, 'extraction'),
        )), 
        label = 'start with',
        description = 'start the simulation with refueling or extraction'
    )
    
    tWaitBeforeExtraction = F.Quantity('Time', default = (50., 's'), minValue = (0., 's'), maxValue=(1.e6, 's'), 
        label = '&#964<sub>extraction</sub>', description = 'waiting time before each extraction')
    tWaitBeforeRefueling = F.Quantity('Time', default = (50., 's'), minValue = (0., 's'), maxValue=(1.e6, 's'), 
        label = '&#964<sub>refueling</sub>', description = 'waiting time before each refueling')
    pMin = F.Quantity('Pressure', default = (20., 'bar'), 
        label = 'p<sub>min</sub>', description = 'minimum pressure in the tank')
    pMax = F.Quantity('Pressure', default = (300., 'bar'), 
        label = 'p<sub>max</sub>', description = 'maximum pressure in the tank')
    mDotExtr = F.Quantity('MassFlowRate', default = (30., 'kg/h'), 
        label = '&#7745<sub>extraction</sub>', description = 'extraction mass flow rate')
    
    hConvTankWaiting = F.Quantity('HeatTransferCoefficient', default = (10, 'W/m**2-K'), 
        label = 'h<sub>conv,waiting</sub>', description = 'tank convection coefficient during waiting time')
    hConvTankExtraction = F.Quantity('HeatTransferCoefficient', default = (20., 'W/m**2-K'), 
        label = 'h<sub>conv,extraction</sub>', description = 'tank convection coefficient during extraction')
    hConvTankRefueling =  F.Quantity('HeatTransferCoefficient', default = (100., 'W/m**2-K'), 
        label = 'h<sub>conv,refueling</sub>', description = 'tank convection coefficient during refueling')
    
    nCompressor = F.Quantity('AngularVelocity', default = (1.0, 'rev/s'), minValue = (0, 'rev/s'), maxValue = (1e4, 'rev/s'),
        label = 'n<sub>compr</sub>', description = 'compressor revolutions')
    
    FG = F.FieldGroup(
        [initialState, pMin, pMax, mDotExtr, tWaitBeforeExtraction, tWaitBeforeRefueling,
         hConvTankWaiting, hConvTankExtraction, hConvTankRefueling,
         nCompressor
        ], 
        label = 'Parameters')
    SG = F.SuperGroup([FG], label = 'Controller')
    
    modelBlocks = []
    
class FluidStateSource(NumericalModel):
    fluid = None
    
    sourceTypeTxt = F.Choices(
        OrderedDict((
            ('TP', 'temperature, pressure'),
            ('PQ', 'pressure, vapour quality'),
            ('TQ', 'temperature, vapour quality'),
        )), 
        label = 'state variables',
        description = 'choose the initial state variables')
    
    @property
    def sourceType(self):
        if self.sourceTypeTxt == 'TP':
            return DM.FluidStateSource.TP
        if self.sourceTypeTxt == 'PQ':
            return DM.FluidStateSource.PQ 
        if self.sourceTypeTxt == 'TQ':
            return DM.FluidStateSource.TQ
        else:
            raise ValueError('Unsupported source type of FluidStateSource.')
    
    T = F.Quantity('Temperature', default = (300, 'K'), 
        label = 'temperature', show = "self.sourceTypeTxt == 'TP' || self.sourceTypeTxt == 'TQ'")
    p = F.Quantity('Pressure', default = (1., 'bar'), 
        label = 'pressure', show = "self.sourceTypeTxt == 'TP' || self.sourceTypeTxt == 'PQ'")
    q = F.Quantity('VaporQuality', default = (0, '-'), minValue = 0, maxValue = 1, 
        label = 'vapour quality', show = "self.sourceTypeTxt == 'TQ' || self.sourceTypeTxt == 'PQ'")
    
    FG = F.FieldGroup([sourceTypeTxt, T, p, q], label = 'Initial values')
        
    modelBlocks = []
    
class Compressor(NumericalModel):
    fluid = None
    
    etaS = F.Quantity('Efficiency', default = (0.9, '-'),
        label = '&#951<sub>S</sub>', description = 'isentropic efficiency')
    fQ = F.Quantity('Fraction', default = (0.1, '-'),
        label = 'f<sub>Q</sub>', description = 'fraction of heat loss to ambient')
    V = F.Quantity('Volume', default = (0.25, 'L'), maxValue = (1e6, 'L'),
        label = 'V<sub>displ</sub>', description = 'displacement volume')
    
    FG = F.FieldGroup([etaS, fQ, V], label = 'Initial values')
    
    modelBlocks = []
    
class FluidChamber(NumericalModel):
    fluid = None
    
    V = F.Quantity('Volume', default = (1., 'L'), maxValue = (1e6, 'L'),
        label = 'volume', description = 'volume')
    TInit = F.Quantity('Temperature', default = (300., 'K'), 
        label = 'initial temperature')
    pInit = F.Quantity('Pressure', default = (1., 'bar'), 
        label = 'initial pressure')
    
    FG = F.FieldGroup([V, TInit, pInit], label = 'Initial values')

    modelBlocks = []
    
class ConvectionHeatTransfer(NumericalModel):
    A = F.Quantity('Area', default = (1., 'm**2'),
        label = 'convection area', description = 'convection area')
    hConv = F.Quantity('HeatTransferCoefficient', default = (10., 'W/m**2-K'),
        label = 'convection coefficient', description = 'convection heat transfer coefficient')
    
    FG = F.FieldGroup([A, hConv], label = 'Initial values')
    
    modelBlocks = []
    
# class SolidConductiveBody(NumericalModel):
#     material = F.ObjectReference(Solids, default = 'StainlessSteel304', 
#         label = 'material', description = 'solid material')
#     mass = F.Quantity('Mass', default = (1., 'kg'), 
#         label = 'mass', description = 'solid mass')
#     thickness = F.Quantity('Length', default = (0.1, 'm'), minValue = (0, 'm'),
#         lable = 'thickness', description = 'solid thickness')
#     conductionArea = F.Quantity('Area', default = (1., 'm**2'),
#         label = 'conduction area', description = 'conduction area')
#     port1Type = F.Choices(portType, 
#         label = 'port-1 type', description = 'choose the type of port-1')
#     port2Type = F.Choices(portType, 
#         label = 'port-1 type', description = 'choose the type of port-2')
#     
#     modelBlocks = []

#         self.composite = DM.SolidConductiveBody(
#             material = 'CarbonFiberComposite', 
#             mass = 34., #[kg]
#             thickness = 0.0105, #[m]
#             conductionArea = params.tankWallArea, #[m**2]
#             port1Type = 'R', port2Type = 'C', 
#             numMassSegments = 4,
#             TInit = 300.0 #[K]
#         )