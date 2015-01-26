'''
Created on Nov 09, 2014
@author: Atanas Pavlov
'''

import numpy as np
from smo.media.CoolProp.CoolProp import FluidState, Fluid
from smo.model.model import NumericalModel, ModelView, ModelDocumentation, HtmlBlock, ModelFigure, ModelDescription
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.MaterialData import Fluids
from collections import OrderedDict

# class ThermodynamicTransition(object):
# 	def __init__(self, inState):
# 		self.inState = inState
# 		self.medium = self.inState.getMedium()
# 		self.outState = FluidState(self.medium)
# 
# class IsentropicCompression(ThermodynamicTransition):
# 	def compute(self, pHigh, etaIsentropic, mDotRefrigerant):
# 		outStateIdeal = FluidState(self.medium)
# 		outStateIdeal.update_ps(pHigh, self.inState.s())
# 		wIdeal = outStateIdeal.h() - self.inState.h()
# 		wReal = wIdeal / etaIsentropic
# 		hOutReal = wReal + self.inState.h()
# 		self.outState.update_ph(pHigh, hOutReal)
# 		self.WCompr = mDotRefrigerant * wReal
# 	@staticmethod
# 	def test():
# 		f = getFluid('ParaHydrogen')
# 		s1 = FluidState(f)
# 		s1.update_Tp(200, 1e5)
# 		compr1 = IsentropicCompression(s1)
# 		compr1.compute(10e5, 1.0, 100./3600)
# 		print compr1.outState.T()
# 		print compr1.WCompr
# 
# class IsothermalCompression(ThermodynamicTransition):
# 	def compute(self, pHigh, etaIsothermal, mDotRefrigerant):
# 		outStateIdeal = MediumState(self.medium)
# 		outStateIdeal.update_Tp(self.T1, self.pHigh)
# 		qIdeal = self.T1 * (self.inState.s() - outStateIdeal.s())
# 		wIdeal = (outStateIdeal.h() - self.inState.h()) + qIdeal
# 		wReal = wIdeal / self.etaComprIsothermal
# 		h2Real = self.inState.h() + wReal - qIdeal
# 		self.outState.update_ph(self.pHigh, h2Real)
#		self.WCompr = self.mDotRefrigerant * wReal

class HeatPump(NumericalModel):
	name = "HeatPump"
	label = "Heat Pump"
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'R134a', label = 'fluid')	
	mDotRefrigerant = Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'refrigerant flow rate')
	pLow = Quantity('Pressure', default = (1, 'bar'), label = 'low pressure')
	pHigh = Quantity('Pressure', default = (10, 'bar'), label = 'high pressure')
	THot = Quantity('Temperature', default = (300, 'K'), label = 'warm temperature')
	TCold = Quantity('Temperature', default = (270, 'K'), label = 'cold temperature')
	compressionType = Choices(
		OrderedDict((
				('isentropic', 'isentropic'),
				('isothermal', 'isothermal')
		)), 
		label = 'compression type')
	etaComprIsentropic = Quantity('Dimensionless', default = 0.8,
		label = 'isentropic efficiency', show = "self.compressionType == 'isentropic'")
	etaComprIsothermal = Quantity('Dimensionless', default = 0.8,
		label = 'isothermal efficiency', show = "self.compressionType == 'isothermal'")
	expansionType = Choices(
		OrderedDict((
				('isenthalpic', 'isenthalpic'),
				('isentropic', 'isentropic')
		)), 
		label = 'expansion type')
	etaExpandIsentropic = Quantity('Dimensionless', default = 0.8,
		label = 'isentropic efficiency', show = "self.expansionType == 'isentropic'")
	basicInputs = FieldGroup([fluidName, mDotRefrigerant, pLow, pHigh, THot, TCold], label = 'Basic')
	compressionExpansion = FieldGroup([compressionType, etaComprIsentropic, etaComprIsothermal, expansionType, etaExpandIsentropic], label = 'Compression/Expansion')
	inputs = SuperGroup([basicInputs, compressionExpansion], label = "Input data")
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	T1 = Quantity('Temperature', label = 'temperature')
	rho1 = Quantity('Density', label = 'density')
	T1Sat = Quantity('Temperature', label = 'saturation temperature')
	compressorInlet = FieldGroup([T1, rho1, T1Sat], label="1. Compressor inlet")
	#####
	T2 = Quantity('Temperature', label = 'temperature')
	rho2 = Quantity('Density', label = 'density')
	WCompr = Quantity('Power', label = 'compressor power')
	T2Sat = Quantity('Temperature', label = 'saturation temperature')
	compressorOutlet = FieldGroup([T2, rho2, WCompr, T2Sat], label="2. Compressor outlet")
	#####
	T3 = Quantity('Temperature', default = (330, 'K'), label = 'temperature')
	rho3 = Quantity('Density', label = 'density')
	QCondens = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'heat flow rate')
	condensorOutlet = FieldGroup([T3, rho3, QCondens], label = '3. Condenser outlet')
	#####
	T4 = Quantity('Temperature', default = (330, 'K'), label = 'temperature')
	q4 = Quantity('VaporQuality', default = 0.5, label = 'vapor quality')
	QEvap = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'heat flow rate')
	evaporatorInlet = FieldGroup([T4, q4, QEvap], label = '4. Evaporator inlet')
	#####
	COPCooling = Quantity('Dimensionless', label = 'COP (cooling)')
	COPHeating = Quantity('Dimensionless', label = 'COP (heating)')
	COPCarnot = Quantity('Dimensionless', label = 'COP (Carnot)')
	summary=FieldGroup([COPCooling, COPHeating, COPCarnot], label = '5. Summary')
	results = SuperGroup([compressorInlet, compressorOutlet, condensorOutlet, evaporatorInlet, summary], label="Results")
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	# Model figure
	figure = ModelFigure(src="ThermoFluids/img/HeatPump.svg")
	
	# Model description
	description = ModelDescription('Heat Pump.', show = False)
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]

	############# Methods ###############
	def compute(self):
		fluid = Fluid(self.fluidName)
		state1 = FluidState(fluid)
		state1Sat = FluidState(fluid)
		state2Ideal = FluidState(fluid)
		state2 = FluidState(fluid)
		state2Sat = FluidState(fluid)
		state3 = FluidState(fluid)
		state4Ideal = FluidState(fluid)
		state4 = FluidState(fluid)
		self.COPCarnot = self.TCold / (self.THot - self.TCold)
		
		# Determine saturation states
		state1Sat.update_pq(self.pLow, 0)
		self.T1Sat = state1Sat.T
		state2Sat.update_pq(self.pHigh, 0)
		self.T2Sat = state2Sat.T
		
		self.T1 = self.TCold
		state1.update_Tp(self.T1, self.pLow)
		self.rho1 = state1.rho
		# Compression
		if (self.compressionType == 'isentropic'):
			sIn = state1.s
			state2Ideal.update_ps(self.pHigh, sIn)
			qIdeal = 0
			wIdeal = state2Ideal.h - state1.h
			wReal = wIdeal / self.etaComprIsentropic
			h2Real = wReal + state1.h
			state2.update_ph(self.pHigh, h2Real)
			self.WCompr = self.mDotRefrigerant * wReal
		elif (self.compressionType == 'isothermal'):
			state2Ideal.update_Tp(self.T1, self.pHigh)
			qIdeal = self.T1 * (state1.s - state2Ideal.s)
			wIdeal = (state2Ideal.h - state1.h) + qIdeal
			wReal = wIdeal / self.etaComprIsothermal
			h2Real = state1.h + wReal - qIdeal
			state2.update_ph(self.pHigh, h2Real)
			self.WCompr = self.mDotRefrigerant * wReal
		else:
			raise ValueError("Compression type must be either 'isentropic' or 'isothermal'")
		self.T2 = state2.T
		self.rho2 = state2.rho
		# Condensation
		self.T3 = self.THot
		state3.update_Tp(self.T3, self.pHigh)
		self.rho3 = state3.rho
		self.QCondens = - self.mDotRefrigerant * (state3.h - state2.h)
		# Expansion
		if (self.expansionType == 'isenthalpic'):
			state4.update_ph(self.pLow, state3.h)
		elif (self.expansionType == 'isentropic'):
			state4Ideal.update_ps(self.pLow, state3.s)
			wExpIdeal = state3.h - state4Ideal.h
			wExpReal = wExpIdeal * self.etaExpandIsentropic
			h4Real = state3.h - wExpReal
			state4.update_ph(self.pLow, h4Real)
		else:
			raise ValueError("Compression type must be either 'isentropic' or 'isothermal'")
		self.T4 = state4.T
		self.q4 = state4.q
		self.QEvap = self.mDotRefrigerant * (state1.h - state4.h)
		self.COPCooling = self.QEvap / self.WCompr
		self.COPHeating = self.QCondens / self.WCompr

class HeatPumpDoc(ModelDocumentation):
	name = 'HeatPumpDoc'
	label = 'Heat Pump (Docs)'
	template = 'documentation/html/HeatPumpDoc.html'
		
if __name__ == '__main__':
	#IsentropicCompression.test()
	pass