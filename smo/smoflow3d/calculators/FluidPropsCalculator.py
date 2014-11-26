'''
Created on Nov 05, 2014
@author: Atanas Pavlov
'''
import numpy as np
from collections import OrderedDict
from smo.numerical_model.model import NumericalModel 
from smo.numerical_model.fields import *
from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState
from smo.smoflow3d.SimpleMaterials import Fluids

StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)')
	))

class FluidPropsCalculator(NumericalModel):
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')	
	stateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
	p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable1 == 'P'")
	T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
	rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
	h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
	s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable1 == 'S'")
	q1 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable1 == 'Q'")
	stateVariable2 = Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
	p2 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
	T2 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
	rho2 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
	h2 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
	s2 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable2 == 'S'")
	q2 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable2 == 'Q'")
	####
	stateGroup1 = FieldGroup([stateVariable1, p1, T1, rho1, h1, s1, q1])
	stateGroup2 = FieldGroup([stateVariable2, p2, T2, rho2, h2, s2, q2, fluidName])
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
		fState = FluidState(self.fluidName)
		fState.update(self.stateVariable1, self.getStateValue(self.stateVariable1, 1), 
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
		fc.fluidName = 'ParaHydrogen'
		fc.stateVariable1 = 'P'
		fc.p1 = 700e5
		fc.stateVariable2 = 'T'
		fc.T2 = 288
		fc.compute()
		print
		print fc.rho

class FluidInfo(NumericalModel):
	crit_p = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
	crit_T = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
	crit_rho = Quantity('Density', default = (1, 'kg/m**3'), label = 'density')
	critPoint = FieldGroup([crit_p, crit_T, crit_rho], label = 'Critical point')

	tripple_p = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
	tripple_T = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
	tripple_rhoV = Quantity('Density', default = (1, 'kg/m**3'), label = 'vapor density')
	tripple_rhoL = Quantity('Density', default = (1, 'kg/m**3'), label = 'liquid density')
	tripplePoint = FieldGroup([tripple_p, tripple_T, tripple_rhoL, tripple_rhoV], label = 'Tripple point')
	
	constants = SuperGroup([critPoint, tripplePoint]) 
	def __init__(self, fluidName):
		f = Fluid(fluidName)
		crit = f.critical()
		self.crit_p = crit['p']
		self.crit_T = crit['T']
		self.crit_rho = crit['rho']

		tripple = f.tripple()
		self.tripple_p = tripple['p']
		self.tripple_T = tripple['T']
		self.tripple_rhoV = tripple['rhoV']
		self.tripple_rhoL = tripple['rhoL']
		
		
	@staticmethod
	def getList(fluidList = None):
		if (fluidList is None):
			fluidList = Fluids
		fluidDataList = []
		for fluid in fluidList:
			fc = FluidInfo(fluid)
			fluidData = {
				'name': fluid,
				'label': Fluids[fluid],
				'constants': fc.superGroupList2Json([fc.constants])
			}
			fluidDataList.append(fluidData)
			
		return fluidDataList
# 	fluidsData = OrderedDict()
# 	for key in Fluids:
# 		fluidsData[key] = {'label' : Fluids[key], 'Constants': [], 'References': []}
# 		f = Fluid(key)
# 		fluidsData[key]['Constants'].append(['Tripple point', list(f.tripple().iteritems())])
# 		fluidsData[key]['Constants'].append(['Critical point', list(f.critical().iteritems())])			
# 		fluidsData[key]['Constants'].append(['Molar mass', [f.molarMass()]])
# # 				fluidsData[key]['Constants']['Accentric factor'] = f.accentricFactor()
# # 				fluidsData[key]['Constants']['Fluid limits'] = f.fluidLimits()
# # 				fluidsData[key]['Constants']['Minimum temperature'] = f.minimumTemperature()
# 		fluidsData[key]['Constants'].append(['CAS', [f.CAS()]])
# 		fluidsData[key]['Constants'].append(['ASHRAE34', [f.ASHRAE34()]])

if __name__ == '__main__':
	FluidPropsCalculator.test()
# 	print getFluidConstants()
# 	print getLiteratureReferences()
