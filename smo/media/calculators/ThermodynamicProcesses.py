from smo.media.CoolProp.CoolProp import FluidState
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.MaterialData import Fluids
from collections import OrderedDict

StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)'),
))

TransitionType = OrderedDict((
	#('P', 'isobaric (const. p)'),
	('T', 'isothermal (const. T)'),
	#('D', 'isochoric (const. v)'),
	('H', 'isenthalpic (const. h)'),
	('S', 'isentropic (const. s)'),
))

class ThermodynamicProcess(object):
	def __init__(self, fluidName, eta = None, heatOutFraction = None):
		self.fluidName = fluidName
		self.initState = FluidState(fluidName)
		self.eta = eta
		self.heatOutFraction = heatOutFraction
		
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]
	
	def compute_process(self, constantStateVariable, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		
		self.T_i = self.initState.T
		self.p_i = self.initState.p
		self.rho_i = self.initState.rho
		self.h_i = self.initState.h
		self.s_i = self.initState.s
		self.q_i = self.initState.q
		self.u_i = self.initState.u
		
		finalState.update(constantStateVariable, self.getStateValue(constantStateVariable, suffix="_i"),
							finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		if self.processType == "expansion":
			self.wReal = self.wIdeal / self.eta
			wExtra = self.wReal - self.wIdeal
		elif self.processType == "compression":
			self.wReal = self.wIdeal * self.eta
			wExtra = self.wIdeal - self.wReal
		self.qOut = wExtra * self.heatOutFraction
		self.qFluid = wExtra * (1 - self.heatOutFraction)
		
		# Real final state
		self.deltaH = self.wIdeal + self.qFluid
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
			
		# Read final state values
		self.T_f = finalState.T
		self.p_f = finalState.p
		self.rho_f = finalState.rho
		self.h_f = finalState.h
		self.s_f = finalState.s
		self.q_f = finalState.q
		self.u_f = finalState.u

		# Compute energy flows
		self.wDotIdeal = self.wIdeal * mDot
		self.wDotReal = self.wReal * mDot
		self.deltaHDot = self.deltaH * mDot
		self.qDotOut = self.qOut * mDot
		self.qDotFluid = self.qFluid * mDot

class IsentropicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"

class IsentropicCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"


# class IsentropicExpansion(object):
# 	def __init__(self, fluidName, eta, heatOutFraction):
# 		self.fluidName = fluidName
# 		self.initState = FluidState(fluidName)
# 		self.eta = eta
# 		self.heatOutFraction = heatOutFraction
# 
# 	def compute_process(self, p_final, mDot):
# 		finalState = FluidState(self.fluidName)
# 		
# 		self.T_i = self.initState.T
# 		self.p_i = self.initState.p
# 		self.rho_i = self.initState.rho
# 		self.h_i = self.initState.h
# 		self.s_i = self.initState.s
# 		self.q_i = self.initState.q
# 		self.u_i = self.initState.u
# 			
# 		# Ideal final state
# 		finalState.update(
# 			'P', 
# 			p_final,
# 			'S',
# 			self.s_i,
# 		)
# 		
# 		# Compute works and heat
# 		self.wIdeal = finalState.h - self.initState.h
# 		self.wReal = self.wIdeal / self.eta
# 		wExtra = self.wReal - self.wIdeal
# 		self.qOut = wExtra * self.heatOutFraction
# 		self.qFluid = wExtra * (1 - self.heatOutFraction)
# 		
# 		# Real final state
# 		self.deltaH = self.wIdeal + self.qFluid
# 		finalState.update(
# 			'P', 
# 			p_final,
# 			'H',
# 			self.initState.h + self.deltaH
# 		)
# 			
# 		# Read final state values
# 		self.T_f = finalState.T
# 		self.p_f = finalState.p
# 		self.rho_f = finalState.rho
# 		self.h_f = finalState.h
# 		self.s_f = finalState.s
# 		self.q_f = finalState.q
# 		self.u_f = finalState.u
# 
# 		# Compute energy flows
# 		self.wDotIdeal = self.wIdeal * mDot
# 		self.wDotReal = self.wReal * mDot
# 		self.deltaHDot = self.deltaH * mDot
# 		self.qDotOut = self.qOut * mDot
# 		self.qDotFluid = self.qFluid * mDot

class HeatingCooling(NumericalModel):
	label = "Heating / Cooling"
	
	############ Inputs ###############
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

	final_T = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
	final_q = Quantity('VaporQuality', label = 'vapor quality')
	finalState = FieldGroup([final_T, final_q], label = 'Final state')
	inputs = SuperGroup([initialState, finalState])
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model View
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	
	# Model View
	resultView = ModelView(ioType = "output", superGroups = [])

	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	############# Methods ###############
	def compute(self):
		pass