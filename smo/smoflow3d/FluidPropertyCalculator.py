'''
Created on Oct 10, 2014

@author: ivaylo
'''
import numpy as np
from smo.smoflow3d.Media import MediumState, Medium

class FluidPropertyCalculator:
    def computeFluidProps(self):
        state1Values = np.linspace(
            self.stateVariable1MinValue, self.stateVariable1MaxValue, 
            self.stateVariable1NumValues, True)
#         rowDType = np.dtype([
#                 ('p', np.float), ('T', np.float),
#                 ('rho', np.float), ('h', np.float),                
#                 ])
        #'s', 'u', 'cp', 'cv', 'dpdt_v', 'dpdv_t', 'dvdt_p', 'beta', 'mu', 'cond', 'Pr', 'gamma' 
        columnNames = ['Pressure', 'Temperature', 'Density', 'Spec. Enthalpy', 
                    'Internal Energy', 'Spec. Heat\nCapacity cp', 'Spec. Heat\nCapacity cv', 
                    '(dp/dt)_v', '(dp/dv)_t', '(dv/dt)_p', 'beta', 
                    'Dyn. viscosity', 'Thermal conductivity', 'Prandtl', 'Gamma']
        tableValues = np.zeros(
            (self.stateVariable1NumValues, len(columnNames)), dtype = float)
        
            
        for i in range(self.stateVariable1NumValues):
            fp = MediumState(fluid)
            fp.update_Tp(state1Values[i], self.stateVariable2Value)
            tableValues[i] = (
                    fp.p(), fp.T(), fp.rho(), fp.h(),
                    fp.u(), fp.cp(), fp.cv(), 
                    fp.dpdt_v(), fp.dpdv_t(), fp.dvdt_p(), fp.beta(),
                    fp.mu(), fp.cond(), fp.Pr(), fp.gamma(), 
                )
        return columnNames, tableValues
