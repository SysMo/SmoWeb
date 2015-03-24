from smo.media.CoolProp.CoolProp import FluidState
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.MaterialData import Fluids
from collections import OrderedDict
from smo.media.diagrams.StateDiagrams import PHDiagram

StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)'),
))

TransitionType = OrderedDict((
	('T', 'isothermal (const. T)'),
	('H', 'isenthalpic (const. h)'),
	('S', 'isentropic (const. s)'),
))


from smo.media.calculators.ThermodynamicProcesses import IsentropicProcess, IsothermalProcess, IsobaricProcess, IsenthalpicExpansion
class ThermodynamicProcessModel(NumericalModel):
	############ Inputs ###############
	fluidName = Choices(options = Fluids, default = 'Water', label = 'fluid')	
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

	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)

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
	delta_h = Quantity('SpecificEnthalpy', label = 'enthalpy change (fluid)') 
	qIn = Quantity('SpecificEnergy', label = "heat in")
	specificEnergyResults = FieldGroup([wIdeal, wReal, delta_h, qIn], label = "Heat/work (specific quantities)")
	# Energy flow quantities
	wDotIdeal = Quantity('Power', label = "ideal work")
	wDotReal = Quantity('Power', label = "real work")
	deltaHDot = Quantity('Power', label = 'enthalpy change (fluid)') 
	qDotIn = Quantity('HeatFlowRate', label = "heat in")
	energyFlowResults = FieldGroup([wDotIdeal, wDotReal, deltaHDot, qDotIn], label = "Heat/work flows")

	energyBalanceResults = SuperGroup([specificEnergyResults, energyFlowResults], label = "Energy balance")
	
	diagram = Image(default='', width=880, height=550)
	diagramViewGroup = ViewGroup([diagram], label = "P-H Diagram")
	diagramSuperGroup = SuperGroup([diagramViewGroup], label = "Diagram")

	# Model View
	resultView = ModelView(ioType = "output", superGroups = [stateResults, energyBalanceResults, diagramSuperGroup])

	############# Page structure ########
	modelBlocks = []

	############# Methods ###############
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]

	def compute(self):
		process = self.computeProcess()
		self.T_i = process.initialState.T
		self.p_i = process.initialState.p
		self.rho_i = process.initialState.rho
		self.h_i = process.initialState.h
		self.s_i = process.initialState.s
		self.q_i = process.initialState.q
		self.u_i = process.initialState.u
		
		
		self.T_f = process.finalState.T
		self.p_f = process.finalState.p
		self.rho_f = process.finalState.rho
		self.h_f = process.finalState.h
		self.s_f = process.finalState.s
		self.q_f = process.finalState.q
		self.u_f = process.finalState.u
		
		self.wIdeal = process.chars.wIdeal
		self.wReal = process.chars.wReal
		self.delta_h = process.chars.delta_h
		self.qIn = process.chars.qIn

		self.wDotIdeal = process.flows.wDotIdeal
		self.wDotReal = process.flows.wDotReal
		self.deltaHDot = process.flows.deltaHDot
		self.qDotIn = process.flows.qDotIn

		diagram = PHDiagram(self.fluidName)
		diagram.setLimits()
		diagramFig  = diagram.draw()
		processFig = process.draw(fig = diagramFig)
		fHandle, resourcePath  = diagram.export(processFig)
		self.diagram = resourcePath
		os.close(fHandle)
		
		
class CompressionExpansionModel(ThermodynamicProcessModel):
	label = "Compression / Expansion"
	description = ModelDescription("Parameteric models for compression/expansion processes: isobaric, isothermal and isenthalpic", show = True)

	transitionType = Choices(options = TransitionType, default = 'S', label = "process type")
	p_final = Quantity('Pressure', default = (10, 'bar'), label = 'pressure')
	eta = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency', show = "self.transitionType != 'H'")
	fQ_S = Quantity(default = 0, minValue = 0, maxValue = 1, label = 'heat loss factor', show="self.transitionType == 'S'")
	fQ_T = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'heat loss factor', show="self.transitionType == 'T'")
	finalState = FieldGroup([transitionType, p_final, eta, fQ_S, fQ_T], label = 'Final state')

	inputs = SuperGroup(['initialState', finalState])
	
	# Model View
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = ThermodynamicProcessModel.inputActionBar, autoFetch = True)

	############# Page structure ########
	modelBlocks = [inputView, 'resultView']

	############# Methods ###############

	def computeProcess(self):
		# Create process
		if self.transitionType == 'S':
			process = IsentropicProcess(self.fluidName, self.eta, self.fQ_S)
		elif self.transitionType == 'H':
			process = IsenthalpicExpansion(self.fluidName)
		elif self.transitionType == 'T':
			process = IsothermalProcess(self.fluidName, self.eta, self.fQ_T)
		# Compute initial state
		process.initialState.update(
				self.stateVariable1, self.getStateValue(self.stateVariable1, suffix = "1"), 
				self.stateVariable2, self.getStateValue(self.stateVariable2, suffix = "2")
		)
		# Compute process
		process.compute(stateVar = 'P', stateVal = self.p_final, mDot = self.mDot)
		return process
		
from smo.media.calculators.ThermodynamicProcesses import HeatingCooling
class HeatingCoolingModel(ThermodynamicProcessModel):
	label = "Heating / Cooling"
	description = ModelDescription("Heating/cooling process at constant pressure", show = True)

	stateVariable_final = Choices(options = OrderedDict((('T', 'temperature (T)'), ('Q', 'vapor quality (Q)'))), 
									default = 'T', label = 'state variable')	
	T_final = Quantity('Temperature', default = (350, 'K'), label = 'temperature', 
					   show="self.stateVariable_final == 'T'")
	q_final = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', 
					  show="self.stateVariable_final == 'Q'")
	finalState = FieldGroup([stateVariable_final, T_final, q_final], label = 'Final state')
	
	inputs = SuperGroup(['initialState', finalState])
	
	# Model View
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = ThermodynamicProcessModel.inputActionBar, autoFetch = True)

	############# Page structure ########
	modelBlocks = [inputView, 'resultView']

	############# Methods ###############

	def computeProcess(self):
		# Create process
		process = IsobaricProcess(self.fluidName)
		# Compute initial state
		process.initialState.update(
				self.stateVariable1, self.getStateValue(self.stateVariable1, suffix = "1"), 
				self.stateVariable2, self.getStateValue(self.stateVariable2, suffix = "2")
		)
		# Compute process
		if (self.stateVariable_final == 'T'):
			process.compute(stateVar = 'T', stateVal = self.T_final, mDot = self.mDot)
		else:
			process.compute(stateVar = 'Q', stateVal = self.q_final, mDot = self.mDot)
		return process
