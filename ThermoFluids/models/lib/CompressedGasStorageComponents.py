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

class Controller(NumericalModel):
    initialState = F.Choices(
        OrderedDict((
            (TC.FUELING, 'fueling'),
            (TC.EXTRACTION, 'extraction'),
        )), 
        label = 'start with',
        description = 'start the simulation with fueling or extraction'
    )
    tWaitBeforeExtraction = F.Quantity('Time', default = (0., 's'), minValue = (0., 's'), maxValue=(1.e6, 's'), 
        label = '&#964 (extraction)', description = 'waiting time before each extraction')
    tWaitBeforeFueling = F.Quantity('Time', default = (0., 's'), minValue = (0., 's'), maxValue=(1.e6, 's'), 
        label = '&#964 (fueling)', description = 'waiting time before each fueling')
    pMin = F.Quantity('Pressure', default = (0., 'bar'), 
        label = 'minimum pressure</sub>', description = 'minimum pressure in the gas storage for starting fueling')
    pMax = F.Quantity('Pressure', default = (0., 'bar'), 
        label = 'maximum pressure', description = 'maximum pressure in the gas storage for stopping fueling')
    mDotExtr = F.Quantity('MassFlowRate', default = (0., 'kg/h'), 
        label = 'extraction mass flow rate', description = 'extraction mass flow rate')
    nCompressor = F.Quantity('AngularVelocity', default = (0., 'rev/s'), minValue = (0, 'rev/s'), maxValue = (1e4, 'rev/s'),
        label = 'compressor speed', description = 'compressor speed')
    
    FG = F.FieldGroup([initialState, pMin, pMax, mDotExtr, nCompressor, tWaitBeforeExtraction, tWaitBeforeFueling], 
        label = 'Parameters')
    
    SG = F.SuperGroup([FG], label = "Parameters") 
    
    modelBlocks = []
    
class FluidStateSource(NumericalModel):
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
    
    T = F.Quantity('Temperature', default = (0., 'degC'), 
        label = 'temperature', description = 'temperature', show = "self.sourceTypeTxt == 'TP' || self.sourceTypeTxt == 'TQ'")
    p = F.Quantity('Pressure', default = (0., 'bar'), 
        label = 'pressure', description = 'pressure', show = "self.sourceTypeTxt == 'TP' || self.sourceTypeTxt == 'PQ'")
    q = F.Quantity('VaporQuality', default = (0., '-'), minValue = 0, maxValue = 1, 
        label = 'vapour quality', description = 'vapour quality', show = "self.sourceTypeTxt == 'TQ' || self.sourceTypeTxt == 'PQ'")
    
    FG = F.FieldGroup([sourceTypeTxt, T, p, q], label = 'Parameters')
        
    modelBlocks = []
    
class Compressor(NumericalModel):   
    etaS = F.Quantity('Efficiency', default = (0., '-'),
        label = 'isentropic efficiency', description = 'isentropic efficiency')
    fQ = F.Quantity('Fraction', default = (0., '-'),
        label = 'heat loss fraction', description = 'heat loss fraction to ambient')
    V = F.Quantity('Volume', default = (0., 'L'), maxValue = (1e6, 'L'),
        label = 'displacement volume', description = 'displacement volume')
    
    FG = F.FieldGroup([etaS, fQ, V], label = 'Parameters')
    
    modelBlocks = []
    
class Cooler(NumericalModel):
    workingState = F.Choices(
        OrderedDict((
            (0, 'off'),
            (1, 'on'),
        )), 
        label = 'state',
        description = 'working state of the cooler')
    
    epsilon = F.Quantity('Efficiency', default = (0., '-'),
        label = 'effectiveness', description = 'effectiveness', show = "self.workingState")
    TCooler = F.Quantity('Temperature', default = (0., 'degC'), 
        label = 'temperature', description = 'temperature', show = "self.workingState")
    
    FG = F.FieldGroup([workingState, epsilon, TCooler], label = 'Parameters')
    
    modelBlocks = []
    
class Tank(NumericalModel):
    wallArea = F.Quantity('Area', default = (0., 'm**2'),
        label = 'wall area', description = 'wall area')
    volume = F.Quantity('Volume', default = (0., 'L'), maxValue = (1e6, 'L'),
        label = 'volume', description = 'volume')
    TInit = F.Quantity('Temperature', default = (0., 'degC'), 
        label = 'initial temperature', description = 'initial temperature')
    pInit = F.Quantity('Pressure', default = (0., 'bar'), 
        label = 'initial pressure', description = 'initial pressure')
    
    linerMaterial = F.ObjectReference(Solids, default = 'StainlessSteel304', 
        label = 'liner material', description = 'liner material')
    linerThickness = F.Quantity('Length', default = (0., 'm'), minValue = (0, 'm'),
        label = 'liner thickness', description = 'liner thickness')
    
    compositeMaterial = F.ObjectReference(Solids, default = 'StainlessSteel304', 
        label = 'composite material', description = 'composite material')
    compositeThickness = F.Quantity('Length', default = (0., 'm'), minValue = (0, 'm'),
        label = 'composite thickness', description = 'composite thickness')
    
    hConvExternal = F.Quantity('HeatTransferCoefficient', default = (0., 'W/m**2-K'), 
        label = 'h<sub>conv</sub> (external)</sub>', description = 'external convection coefficient to ambient')
    hConvInternalWaiting = F.Quantity('HeatTransferCoefficient', default = (0., 'W/m**2-K'), 
        label = 'h<sub>conv</sub> (internal,waiting)</sub>', description = 'internal convection coefficient during waiting time')
    hConvInternalExtraction = F.Quantity('HeatTransferCoefficient', default = (0., 'W/m**2-K'), 
        label = 'h<sub>conv</sub> (internal, extraction)</sub>', description = 'internal convection coefficient during extraction')
    hConvInternalFueling =  F.Quantity('HeatTransferCoefficient', default = (0., 'W/m**2-K'), 
        label = 'h<sub>conv</sub> (internal, fueling)', description = 'internal convection coefficient during refueling')


    initialValuesFG = F.FieldGroup([wallArea, volume, TInit, pInit], 
        label = 'Initial values')
    convectionFG = F.FieldGroup([hConvExternal, hConvInternalWaiting, hConvInternalExtraction, hConvInternalFueling], 
        label = 'Convection')
    linerFG = F.FieldGroup([linerMaterial, linerThickness], 
        label = 'Liner')
    compositeFG = F.FieldGroup([compositeMaterial, compositeThickness],
        label = 'Composite')
        
    SG = F.SuperGroup([initialValuesFG, convectionFG, linerFG, compositeFG], label = "Parameters")
    
    modelBlocks = []