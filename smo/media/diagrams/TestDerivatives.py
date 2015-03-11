'''
Created on Feb 23, 2015

@author: Atanas Pavlov
'''

import numpy as np
from smo.media.CoolProp.CoolProp import FluidState, Fluid

fluid = Fluid('Water')

dT = 1e-4
dq = 1e-3

f1 = FluidState(fluid)
f2 = FluidState(fluid)

f1.update_Tq(273.15 + 150, 0.5)

# dqdT_v
f2.update_Trho(f1.T + dT, f1.rho)
dqdT_v = (f2.q - f1.q) / (f2.T - f1.T)
print ("dqdT_v() numerical: {:e}, analytical: {:e}".format(dqdT_v, f1.dqdT_v)) 

# dvdT_q
f2.update_Tq(f1.T + dT, f1.q)
dvdT_q = (f2.v - f1.v) / (f2.T - f1.T)
dvdT_q_1 = f1.q * f1.SatV.dvdT + (1 - f1.q) * f1.SatL.dvdT
print ("dvdT_q() numerical: {:e}, analytical: {:e}, analytical2: {:e}".format(dvdT_q, f1.dvdT_q, dvdT_q_1))

# dvdq_T
f2.update_Tq(f1.T, f1.q + dq) 
dvdq_T = (f2.v - f1.v) / (f2.q - f1.q)
print ("dvdq_T() numerical: {:e}, analytical: {:e}".format(dvdq_T, f1.dvdq_T))

# dsdT_q
f2.update_Tq(f1.T + dT, f1.q)
dsdT_q = (f2.s - f1.s) / (f2.T - f1.T)
print ("dsdT_q() numerical: {:e}, analytical: {:e}".format(dsdT_q, f1.dsdT_q))


h2 = FluidState("Water")
h2.update_pq(1e5, 0.5)
print h2.SatV.h

############################
class DerivativeTest:
    def __init__ (self, fluid):
        self.fluid = fluid
        self.fState = FluidState(self.fluid)

    def numerical_derivative(self, stateVarNum,
                                    stateVarDenom, stateVarDenom_val, delta = 1.000001, 
                                    stateVarConst, stateVarConst_val):
        """
        stateVarNum - name of state variable in numerator of the derivative (name is in style of FluidState properties)
        stateVarDenom - name of state variable in denominator of the derivative (name is in style of FluidState.update arguments)
        stateVarConst - name of constant state variable (name is in style of FluidState.update arguments)
        """
        self.fState.update(stateVarDenom, stateVarDenom_val, stateVarConst, stateVarConst_val)
        stateVarNum_val = getattr(self.fState, stateVarNum)
        stateVarDenom_val_new = stateVarDenom_val * delta
        self.fState.update(stateVarDenom, stateVarDenom_val_new, stateVarConst, stateVarConst_val)
        stateVarNum_val_new = getattr(self.fState, stateVarNum)
        num_derivative = (stateVarNum_val_new - stateVarNum_val) / (stateVarDenom_val_new - stateVarDenom_val)
        return num_derivative
    
    @staticmethod
    def test():
        test_instance = DerivativeTest("Water")
        _drhodT_s = test_instance.numerical_derivative('rho', 
                                                     'T', 633.15,
                                                     'S', 4000)
        print ('Numerical: ' + str(_drhodT_s))
        fState = FluidState("Water")
        fState.update_Ts(633.15, 4000)
        print ('Analytical: ' + str(fState.rho**2 * fState.dsdT_v / fState.dpdT_v))
        print ('q = {}'.format(fState.q))

if __name__ == '__main__':
    DerivativeTest.test()