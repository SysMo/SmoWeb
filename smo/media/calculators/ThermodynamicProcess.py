import numpy as np
from smo.media.CoolProp.CoolProp import FluidState, Fluid
from smo.model.model import NumericalModel, ModelView, RestBlock
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.MaterialData import Fluids
from collections import OrderedDict
from django.views.decorators.http import etag

StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)'),
))

TransitionType = OrderedDict((
	('P', 'isobaric (const. p)'),
	('T', 'isothermal (const. T)'),
	('D', 'isochoric (const. v)'),
	('H', 'isenthalpic (const. h)'),
	('S', 'isentropic (const. s)'),
))

class ThermodynamicProcess(NumericalModel):
	name = "ThermodynamicProcess"
	label = "Thermodynamic processes"
	
	# 1. ############ Inputs ###############
	# 1.1 Input values
	
	fluidName = Choices(options = Fluids, default = 'ParaHydrogen', label = 'fluid')	
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
	mDot = Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mass flow')
	initialState = FieldGroup([fluidName, stateVariable1, p1, T1, rho1, h1, s1, q1, stateVariable2, p2, T2, rho2, h2, s2, q2, mDot], label = 'Initial state')

	transitionType = Choices(options = TransitionType, default = 'S', label = "process type")
	final_StateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')	
	final_p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="(self.final_StateVariable1 == 'P') && (self.transitionType != 'P')")
	final_T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="(self.final_StateVariable1 == 'T') && (self.transitionType != 'T')")
	final_rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="(self.final_StateVariable1 == 'D') && (self.transitionType != 'D')")
	final_h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="(self.final_StateVariable1 == 'H') && (self.transitionType != 'H')")
	eta = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency')
	heatOutFraction = Quantity(default = 0.1, minValue = 0, maxValue = 1, label = 'released heat fraction')
	finalState = FieldGroup([transitionType, final_StateVariable1, final_p1, final_T1, final_rho1, final_h1, eta, heatOutFraction], label = 'Final state')
	
	inputs = SuperGroup([initialState, finalState])
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model View
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)

	############# Results ###############
	# Initial state
	T_i = Quantity('Temperature', label = 'temperature')
	p_i = Quantity('Pressure', label = 'pressure')
	rho_i = Quantity('Density', label = 'density')
	h_i = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
	s_i = Quantity('SpecificEntropy', label = 'specific entropy')
	q_i = Quantity('VaporQuality', label = 'vapor quality')
	u_i = Quantity('SpecificInternalEnergy', label = 'specific internal energy')	
	initialStateResults = FieldGroup([T_i, p_i, rho_i, h_i, s_i, q_i, u_i], label = 'Initial state')

	# Final state
	T_f = Quantity('Temperature', label = 'temperature')
	p_f = Quantity('Pressure', label = 'pressure')
	rho_f = Quantity('Density', label = 'density')
	h_f = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
	s_f = Quantity('SpecificEntropy', label = 'specific entropy')
	q_f = Quantity('VaporQuality', label = 'vapor quality')
	u_f = Quantity('SpecificInternalEnergy', label = 'specific internal energy')	
	finalStateResults = FieldGroup([T_f, p_f, rho_f, h_f, s_f, q_f, u_f], label = 'Final state')
	
	stateResults = SuperGroup([initialStateResults, finalStateResults], label = "States")
	# Specific enetry quantities
	wIdeal = Quantity('SpecificEnergy', label = "ideal work")
	wReal = Quantity('SpecificEnergy', label = "real work")
	deltaH = Quantity('SpecificEnthalpy', label = 'enthalpy change (fluid)') 
	qOut = Quantity('SpecificEnergy', label = "heat released")
	qFluid = Quantity('SpecificEnergy', label = "heat to fluid")
	specificEnergyResults = FieldGroup([wIdeal, wReal, deltaH, qOut, qFluid], label = "Heat/work (specific quantities)")
	# Energy flow quantities
	wDotIdeal = Quantity('Power', label = "ideal work")
	wDotReal = Quantity('Power', label = "real work")
	deltaHDot = Quantity('Power', label = 'enthalpy change (fluid)') 
	qDotOut = Quantity('HeatFlowRate', label = "heat released")
	qDotFluid = Quantity('HeatFlowRate', label = "heat to fluid")
	energyFlowResults = FieldGroup([wDotIdeal, wDotReal, deltaHDot, qDotOut, qDotFluid], label = "Heat/work flows")

	energyBalanceResults = SuperGroup([specificEnergyResults, energyFlowResults], label = "Energy balance")
	
	# Model View
	resultView = ModelView(ioType = "output", superGroups = [stateResults, energyBalanceResults])

	############# Page structure ########
	modelBlocks = [inputView, resultView]

	############# Methods ###############
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]

	def compute(self):
		initState = FluidState(self.fluidName)
		finalState = FluidState(self.fluidName)

		# Compute initial state
		initState.update(
				self.stateVariable1, self.getStateValue(self.stateVariable1, suffix = "1"), 
				self.stateVariable2, self.getStateValue(self.stateVariable2, suffix = "2")
		)
		self.T_i = initState.T
		self.p_i = initState.p
		self.rho_i = initState.rho
		self.h_i = initState.h
		self.s_i = initState.s
		self.q_i = initState.q
		self.u_i = initState.u


		if (self.transitionType == 'S'):
			# Ideal final state
			finalState.update(
				self.final_StateVariable1, 
				self.getStateValue(self.final_StateVariable1, prefix = 'final_', suffix = "1"),
				'S',
				initState.s
			)
			
			# Compute works and heat
			self.wIdeal = finalState.h - initState.h
			self.wReal = self.wIdeal / self.eta
			wExtra = self.wReal - self.wIdeal
			self.qOut = wExtra * self.heatOutFraction
			self.qFluid = wExtra * (1 - self.heatOutFraction)
			
			# Real final state
			self.deltaH = self.wIdeal + self.qFluid
			finalState.update(
				self.final_StateVariable1,
				self.getStateValue(self.final_StateVariable1, prefix = 'final_', suffix = "1"),
				'H',
				initState.h + self.deltaH
			)
		else:
			raise ValueError("Unimplemented process type '{0}'".format(TransitionType[self.transitionType]))
			
		# Read final state values
		self.T_f = finalState.T
		self.p_f = finalState.p
		self.rho_f = finalState.rho
		self.h_f = finalState.h
		self.s_f = finalState.s
		self.q_f = finalState.q
		self.u_f = finalState.u

		# Compute energy flows
		self.wDotIdeal = self.wIdeal * self.mDot
		self.wDotReal = self.wReal * self.mDot
		self.deltaHDot = self.deltaH * self.mDot
		self.qDotOut = self.qOut * self.mDot
		self.qDotFluid = self.qFluid * self.mDot
