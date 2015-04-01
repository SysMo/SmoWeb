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
    
    parametersFG = F.FieldGroup(
        [initialState, pMin, pMax, mDotExtr, tWaitBeforeExtraction, tWaitBeforeRefueling,
         hConvTankWaiting, hConvTankExtraction, hConvTankRefueling,
         nCompressor
        ], 
        label = 'Parameters')
    SG = F.SuperGroup([parametersFG], label = 'Controller')
    
    modelBlocks = []
    
class FluidStateSource(NumericalModel):
    fluid = None
    
    sourceTypeTxt = F.Choices(
        OrderedDict((
            ('PQ', 'pressure, vapour quality'),
            ('TP', 'temperature, pressure'),
            ('TQ', 'temperature, vapour quality'),
        )), 
        label = 'state variables',
        description = 'choose the initial state variables'
    )
    
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
    
    T = F.Quantity('Temperature', default = (15, 'K'), label = 'temperature', 
        show = "self.sourceTypeTxt == 'TP' || self.sourceTypeTxt == 'TQ'")
    p = F.Quantity('Pressure', default = (2., 'bar'), label = 'pressure',
        show = "self.sourceTypeTxt == 'TP' || self.sourceTypeTxt == 'PQ'")
    q = F.Quantity('VaporQuality', default = (0, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', 
        show = "self.sourceTypeTxt == 'TQ' || self.sourceTypeTxt == 'PQ'")
    
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
    