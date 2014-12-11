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
from smo.smoflow3d.CoolProp.CoolPropReferences import References

StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)')
	))

referenceKeys = OrderedDict((
	('EOS', 'Equation of State'), 
	('CP0', 'CP0 reference'),
	('VISCOSITY', 'Viscosity'),
	('CONDUCTIVITY', 'Conductivity'),
	('ECS_LENNARD_JONES', 'Lennard-Jones Parameters for ECS'),
	('ECS_FITS', 'ECS_FITS reference'),
	('SURFACE_TENSION', 'Surface Tension')
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
		self.T = fState.T
		self.p = fState.p
		self.rho = fState.rho
		self.h = fState.h
		self.s = fState.s
		self.q = fState.q
		self.u = fState.u
		
		self.cp = fState.cp
		self.cv = fState.cv
		self.gamma = fState.gamma
		self.Pr = fState.Pr
		self.cond = fState.cond
		self.mu = fState.mu
		self.dpdt_v = fState.dpdt_v
		self.dpdv_t = fState.dpdv_t
			
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
	
	t_max = Quantity('Temperature', default = (300, 'K'), label = 'Max. temperature')
	rho_max = Quantity('Density', label = 'Max. density')
	t_min = Quantity('Temperature', default = (300, 'K'), label = 'Min. temperature')
	p_max = Quantity('Pressure', default = (1, 'bar'), label = 'Max. pressure')
	fluidLimits = FieldGroup([t_max, rho_max, t_min, p_max], label = 'Fluid limits')
	
	molar_mass = Quantity('MolarMass', label = 'molar mass')
	accentric_factor = Quantity('Dimensionless', label = 'accentric factor')
	cas = String('CAS', label = 'CAS')
	ashrae34 = String('ASHRAE34', label = 'ASHRAE34')
	other = FieldGroup([molar_mass, accentric_factor, cas, ashrae34], label = 'Other')
	
	constants = SuperGroup([critPoint, tripplePoint, fluidLimits, other])
	
	def __init__(self, fluidName):
		f = Fluid(fluidName)
		crit = f.critical
		self.crit_p = crit['p']
		self.crit_T = crit['T']
		self.crit_rho = crit['rho']

		tripple = f.tripple
		self.tripple_p = tripple['p']
		self.tripple_T = tripple['T']
		self.tripple_rhoV = tripple['rhoV']
		self.tripple_rhoL = tripple['rhoL']
		
		fLimits = f.fluidLimits
		self.t_max = fLimits['TMax']
		self.rho_max = fLimits['rhoMax']
		self.t_min = fLimits['TMin']
		self.p_max = fLimits['pMax']
		
		self.molar_mass = f.molarMass*10**-3
		self.accentric_factor = f.accentricFactor
		self.cas = f.CAS
		self.ashrae34 = f.ASHRAE34
		
	def getReferences(self, fluidName):
		f = Fluid(fluidName)
		refList = []
		for key in referenceKeys:
			try:
				reference = References[f.BibTeXKey(key)]
			except KeyError:
				reference = None
			refList.append([referenceKeys[key], reference])
		return refList
		
	@staticmethod
	def getFluidInfo(fluidList = None):
		if (fluidList is None):
			fluidList = Fluids
		fluidInformation = []
		for fluid in fluidList:
			fi = FluidInfo(fluid)
			fluidData = {
				'name': fluid,
				'label': Fluids[fluid],
				'constants': fi.superGroupList2Json([fi.constants]),
				'references': fi.getReferences(fluid)
			}
			fluidInformation.append(fluidData)		
		return fluidInformation
	
	@staticmethod
	def getFluidList():
		fluidList = []
		for fluid in Fluids:
			fluidList.append([fluid, Fluids[fluid]])
		return fluidList
			
	@staticmethod
	def test():
		print FluidInfo.getFluidList()

class SaturationData(NumericalModel):	
	fluidName = String(default = 'ParaHydrogen', label = 'fluid')
	T_p_satPlot = PlotView(options = {'title': 'T(p) Sat Plot', 'labels': ['pressure [bar]', 'T sat [K]']})
	rho_p_satPlot = PlotView(options = {'title': 'rho(p) Sat Plot', 'labels': ['pressure [bar]', 'rho_L sat [kg/m**3]', 'rho_V sat [kg/m**3]']})
	delta_h_p_satPlot = PlotView(options = {'title': 'delta_h(p) Sat Plot', 'labels': ['pressure [bar]', 'delta_h sat [J]']})
	delta_s_p_satPlot = PlotView(options = {'title': 'delta_s(p) Sat Plot', 'labels': ['pressure [bar]', 'delta_s sat [J]']})
	
	satTableView = TableView(options = {'title': 'Sat Table', 'formats': ['0.00E0', '#.00']})	
	satViewGroup = ViewGroup([T_p_satPlot, rho_p_satPlot, delta_h_p_satPlot, delta_s_p_satPlot,
								satTableView], label="Saturation Data")
	satSuperGroup = SuperGroup([satViewGroup])
	
	def compute(self):
		f = Fluid(self.fluidName)
		fState = FluidState(self.fluidName)
		
		pressures = np.logspace(np.log10(f.tripple['p']), np.log10(f.critical['p']), 100, endpoint = False)/1e5
		T_list = []
		rhoL_list = []
		rhoV_list = []
		hL_list = []
		hV_list = []
		sL_list = []
		sV_list = []
		data = []
		
		for p in pressures:
			fState.update_pq(p*1e5, 0)			
			satL = fState.getSatL()			
			satV = fState.getSatV()
			
			T_list.append(fState.T)
			rhoL_list.append(satL['rho'])
			rhoV_list.append(satV['rho'])
			hL_list.append(satL['h'])
			hV_list.append(satV['h'])
			sL_list.append(satL['s'])
			sV_list.append(satV['s'])
						
			data.append([p, fState.T, satL['rho'], satL['s'], satL['h'], 
						satV['rho'], satV['s'], satV['h']])
		
		viewContentObj = ViewContent(data = np.array([[p, T] for (p, T) in zip(pressures, T_list)]), columnLabels = ['p [bar]', 'T [K]'])		
		self.T_p_satPlot = viewContentObj
		
		viewContentObj = ViewContent(data = np.array([[p, rhoL, rhoV] for (p, rhoL, rhoV) in zip(pressures, rhoL_list, rhoV_list)]), columnLabels = ['p [bar]', 'rho_L [kg/m**3]',
																											'rho_V [kg/m**3]'])
		self.rho_p_satPlot = viewContentObj
		
		viewContentObj = ViewContent(data = np.array([[p, hV - hL] for (p, hV, hL) in zip(pressures, hV_list, hL_list)]), columnLabels = ['p [bar]', 'delta_h [J]'])
		self.delta_h_p_satPlot = viewContentObj
		
		viewContentObj = ViewContent(data = np.array([[p, sV - sL] for (p, sV, sL) in zip(pressures, sV_list, sL_list)]), columnLabels = ['p [bar]', 'delta_s [J]'])
		self.delta_s_p_satPlot = viewContentObj
		
		viewContentObj = ViewContent(data = np.array(data), columnLabels = ['p [bar]', 'T [K]', 
																			'rho_L [kg/m**3]', 's_L [J]', 'h_L [J]',
																		'rho_V [kg/m**3]', 's_V [J]', 'h_V [J]'])
		self.satTableView = viewContentObj
		
if __name__ == '__main__':
# 	FluidPropsCalculator.test()
# 	print getFluidConstants()
# 	print getLiteratureReferences()
	FluidInfo.test()
