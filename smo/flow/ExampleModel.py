from smo.model.model import NumericalModel
from smo.model.fields import *
import numpy as np
from smo.media.SimpleMaterials import Fluids
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict


class ExampleModel(NumericalModel):
    p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
    T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
    inputsArray = RecordArray(OrderedDict((
                                ('inputs', Quantity()),       
                            )), label='input array')
    ####
    inputFieldGroup = FieldGroup([inputsArray], label = 'Input Field Group')
    inputSuperGroup = SuperGroup([inputFieldGroup], label= 'Input Super Group')
    ####
    
    x = Quantity(label = 'product')
    resultsFieldGroup = FieldGroup([x], label = 'Results Field Group')
    resultsSuperGroup = SuperGroup([resultsFieldGroup], label= 'Results Super Group')
    
    def compute(self):
        print type(np.prod(self.inputsArray['inputs']))
        self.x = np.prod(self.inputsArray['inputs'])