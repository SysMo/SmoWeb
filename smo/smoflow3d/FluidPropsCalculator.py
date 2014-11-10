'''
Created on Nov 05, 2014
@author: Atanas Pavlov
'''
import numpy as np
from collections import OrderedDict
from smo.smoflow3d.Media import MediumState, Medium
from smo.smoflow3d import getFluid
from smo.numerical_model.model import NumericalModel 
from smo.numerical_model.fields import *
from smo.smoflow3d.SimpleMaterials import Fluids

StateVariableOptions = OrderedDict(
	(('P', 'pressure'),
	('T', 'temperature'),
	('D', 'density'),
	('H', 'specific enthalpy'),
	('S', 'specific entropy'),
	('Q', 'vapor quality'))
)

class FluidPropsCalculator(NumericalModel):
	fluid = ObjectReference(Fluids, default = 'ParaHydrogen', label = 'fluid')	
	stateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
	p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable1 == 'P'")
	T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
	rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
	h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
	s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable1 == 'S'")
	q1 = Quantity('VaporQuality', default = (1, '-'), label = 'vapour quality', show="self.stateVariable1 == 'Q'")
	stateVariable2 = Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
	p2 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
	T2 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
	rho2 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
	h2 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
	s2 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable2 == 'S'")
	q2 = Quantity('VaporQuality', default = (1, '-'), label = 'vapour quality', show="self.stateVariable2 == 'Q'")
	####
	stateGroup1 = FieldGroup([stateVariable1, p1, T1, rho1, h1, s1, q1])
	stateGroup2 = FieldGroup([stateVariable2, p2, T2, rho2, h2, s2, q2, fluid])
	inputs = SuperGroup([stateGroup1, stateGroup2], label='State inputs')
	####
	T = Quantity('Temperature', label = 'temperature')
	p = Quantity('Pressure', label = 'pressure')
	rho = Quantity('Density', label = 'density')
	h = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
	s = Quantity('SpecificEntropy', label = 'specific entropy')
	q = Quantity('VaporQuality', label = 'vapor quality')
	u = Quantity('SpecificInternalEnergy', label = 'specific internal energy')
	stateVariablesResults = FieldGroup([T, p, rho, h, s, q, u])
	#####
	cp = Quantity('SpecificHeatCapacity', label = 'heat capacity (cp)')
	cv = Quantity('SpecificHeatCapacity', label = 'heat capacity (cv)')	
	gamma = Quantity('Dimensionless', label = 'gamma = cp/cv')
# 	beta = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
# 	alpha = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	mu = Quantity('DynamicViscosity', label = 'dynamic viscosity')
	dpdt_v = Quantity('Dimensionless', label = '(dp/dT)<sub>v</sub>')
	dpdv_t = Quantity('Dimensionless', label = '(dp/dv)<sub>T</sub>')
	derivativeResults = FieldGroup([cp, cv, gamma, Pr, cond, mu, dpdt_v, dpdv_t])
	###
	results = SuperGroup([stateVariablesResults, derivativeResults], label="Computed properties")
	def getStateValue(self, sVar, index):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[sVarDict[sVar]+str(index)]
			
	def compute(self):
		fluid = getFluid(str(self.fluid['_key']))
		fState = MediumState(fluid)
		fState.update_state(self.stateVariable1, self.getStateValue(self.stateVariable1, 1), 
						self.stateVariable2, self.getStateValue(self.stateVariable2, 2))
		self.T = fState.T()
		self.p = fState.p()
		self.rho = fState.rho()
		self.h = fState.h()
		self.s = fState.s()
		self.q = fState.q()
		self.u = fState.u()
		
		self.cp = fState.cp()
		self.cv = fState.cv()
		self.gamma = fState.gamma()
		self.Pr = fState.Pr()
		self.cond = fState.cond()
		self.mu = fState.mu()
		self.dpdt_v = fState.dpdt_v()
		self.dpdv_t = fState.dpdv_t()
	
	@staticmethod	
	def test():
		fc = FluidPropsCalculator()
		fc.fluid = 'ParaHydrogen'
		fc.stateVariable1 = 'P'
		fc.p1 = 700e5
		fc.stateVariable2 = 'T'
		fc.T2 = 288
		fc.compute()
		print
		print fc.rho

if __name__ == '__main__':
	FluidPropsCalculator.test()