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
#dvdT_q_1 = f1.q * f1.SatV.drhodT / 
print ("dvdT_q() numerical: {:e}, analytical: {:e}".format(dvdT_q, f1.dvdT_q))

# dvdq_T
f2.update_Tq(f1.T, f1.q + dq) 
dvdq_T = (f2.v - f1.v) / (f2.q - f1.q)
print ("dvdq_T() numerical: {:e}, analytical: {:e}".format(dvdq_T, f1.dvdq_T))

# dsdT_q
f2.update_Tq(f1.T + dT, f1.q)
dsdT_q = (f2.s - f1.s) / (f2.T - f1.T)
print ("dsdT_q() numerical: {:e}, analytical: {:e}".format(dsdT_q, f1.dsdT_q))
