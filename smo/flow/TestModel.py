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
    testArray = RecordArray(
        OrderedDict((
                     ('p', Quantity('Pressure', default = (1, 'bar'), label = 'pressure')),
                     ('T', Quantity('Temperature', default = (300, 'K'), label = 'temperature')),
                     ('rho', Quantity('Density', default = (1, 'kg/m**3'), label = 'density'))
                     )),
        numRows=7, label="testArray")
    testFieldGroup = FieldGroup([h1, s1, testArray, p, T], label = "testFieldGroup")
    testSuperGroup = SuperGroup([testFieldGroup], label = "testSuperGroup")
    
    @classmethod
    def test(cls):
        t = TestModel()
        print TestModel.p
        print t.p
# if __name__ == '__main__':
#     FluidPropsCalculator.test()
#     print getFluidConstants()
#     print getLiteratureReferences()