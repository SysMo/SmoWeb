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
    testStr = String(label="testStr", default="blaah")
    ####
    testArray = RecordArray(
        OrderedDict((
                     ('p', Quantity('Pressure', default = (1, 'bar'), label = 'pressure')),
                     ('T', Quantity('Temperature', default = (300, 'K'), label = 'temperature')),
                     ('rho', Quantity('Density', default = (1, 'kg/m**3'), label = 'density')),
                     ('fluid', Choices(Fluids, default = 'ParaHydrogen', label = 'fluid'))
                     )),
        numRows=7, label="testArray")
    
    testArray2 = RecordArray(
        OrderedDict((
                     ('p', Quantity('Pressure', default = (1, 'bar'), label = 'pressure')),
                     ('rho', Quantity('Density', default = (1, 'kg/m**3'), label = 'density')),
                     ('film T', Boolean(default = False, label = '')),
                     ('comment', String(label="str", default="string placeholder"))
                     )),
        numRows=3, label="testArray2")
    
    testFieldGroup = FieldGroup([h1, s1, testArray, p], label = "testFieldGroup")
    testFieldGroup2 = FieldGroup([testStr, testArray2, T], label = "testFieldGroup2")
    testSuperGroup = SuperGroup([testFieldGroup, testFieldGroup2], label = "testSuperGroup")
    
    @classmethod
    def test(cls):
        t = TestModel()
        print t.testArray2
if __name__ == '__main__':
    TestModel.test()