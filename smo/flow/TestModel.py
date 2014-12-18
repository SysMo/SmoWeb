from smo.model.model import NumericalModel
from smo.model.fields import *
import numpy as np
from smo.media.SimpleMaterials import Fluids
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict

class TestModel(NumericalModel):
    p = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
    T = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
    rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density')
    h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy')
    s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy')
    ####
    testArray = ArrayGroup(Record(
        OrderedDict((
                     ('p', Quantity('Pressure', default = (1, 'bar'), label = 'pressure')),
                     ('T', Quantity('Temperature', default = (300, 'K'), label = 'temperature')),
                     ('rho', Quantity('Density', default = (1, 'kg/m**3'), label = 'density'))
                     ))), 
        numRows=7, label="testArray")
    testSuperGroup = SuperGroup([testArray], label = "testSuperGroup")
    
# if __name__ == '__main__':
#     FluidPropsCalculator.test()
#     print getFluidConstants()
#     print getLiteratureReferences()