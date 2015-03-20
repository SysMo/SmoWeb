'''
Created on Nov 09, 2014
@author: Atanas Pavlov
'''

import numpy as np
from smo.media.CoolProp.CoolProp import FluidState, Fluid
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.web.blocks import HtmlBlock
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
	label = "Heat Pump"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/HeatPump.svg")
	description = ModelDescription("Simple model of a heat pump. Could be used to calculate air-conditioners or refrigerators", show = True)

# 	description = ModelDescription('Heat Pump.', show = False)
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'R134a', label = 'fluid')	
	mDotRefrigerant = Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'refrigerant flow rate')
	pLow = Quantity('Pressure', default = (1, 'bar'), label = 'low pressure')
	pHigh = Quantity('Pressure', default = (10, 'bar'), label = 'high pressure')
	THot = Quantity('Temperature', default = (300, 'K'), label = 'condenser temperature')
	TCold = Quantity('Temperature', default = (270, 'K'), label = 'evaporator temperature')
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

from processes import ReverseBraytonCycle, CompressorOneStage, IsobaricHeatExchanger
from smo.media.diagrams.StateDiagrams import PHDiagram
class ReverseBraytonCycleModel(NumericalModel):
	label = "Reverse Brayton Cycle"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/HeatPump.svg")
	description = ModelDescription("Basic Brayton cycle used in refrigerators and air conditioners")

	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	fluidName = Choices(Fluids, default = 'R134a', label = 'fluid')	
	mDotRefrigerant = Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'refrigerant flow rate')
	refrigerantInputs = FieldGroup([fluidName, mDotRefrigerant], 'Refrigerant')
	# FieldGroup
	compressorModelType = Choices(OrderedDict((
		('S', 'isentropic'),
		('T', 'isothermal'),
	)), label = 'compressor model')
	etaCompressor = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency', show = "self.compressorModelType == 'S'")
	fQCompressor = Quantity(default = 0, minValue = 0, maxValue = 1, label = 'heat loss factor', show="self.compressorModelType == 'S'")
	compressorInputs = FieldGroup([compressorModelType, etaCompressor, fQCompressor], label = 'Compressor')
	# FieldGroup
	TCondensation = Quantity('Temperature', default = (40, 'degC'), label = 'condensation temperature')
	condenserOutletStateChoice = Choices(OrderedDict((
		('eta', 'thermal efficiency'),
		('dT', 'sub-cooling'),
		('Q', 'vapor quality'),
		('T', 'temperature'),
		('H', 'enthalpy'),
	)), label = 'compute outlet by')
	etaCondenser = Quantity(default = 0.9, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.condenserOutletStateChoice == "eta"')
	TExtCondenser = Quantity('Temperature', default = (30, 'degC'), label = 'external temperature', show = 'self.condenserOutletStateChoice == "eta"')
	dTOutletCondenser = Quantity('TemperatureDifference', default = (-5, 'degC'), minValue = -1e10, maxValue = -1e-3, label = 'outlet subcooling', show = 'self.condenserOutletStateChoice == "dT"')
	qOutletCondenser = Quantity(default = 0, minValue = 0, maxValue = 1, label = 'outlet vapor quality', show = 'self.condenserOutletStateChoice == "Q"')
	TOutletCondenser = Quantity('Temperature', default = (40, 'degC'), label = 'outlet temperature', show = 'self.condenserOutletStateChoice == "T"')
	hOutletCondenser = Quantity('SpecificEnthalpy', default = (100, 'kJ/kg'), minValue = -1e10, label = 'outlet enthalpy', show = 'self.condenserOutletStateChoice == "H"')
	
	condenserInputs = FieldGroup([TCondensation, condenserOutletStateChoice, etaCondenser, TExtCondenser, dTOutletCondenser, 
			TOutletCondenser, qOutletCondenser, hOutletCondenser], 
			label = 'Condensor')

	# FieldGroup
	TEvaporation = Quantity('Temperature', default = (-10, 'degC'), label = 'evaporation temperature')
	evaporatorOutletStateChoice = Choices(OrderedDict((
		('eta', 'thermal efficiency'),
		('dT', 'super-heating'),
		('Q', 'vapor quality'),
		('T', 'temperature'),
		('H', 'enthalpy'),
	)), label = 'compute outlet by')
	etaEvaporator = Quantity(default = 0.9, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.evaporatorOutletStateChoice == "eta"')
	TExtEvaporator = Quantity('Temperature', default = (0, 'degC'), label = 'external temperature', show = 'self.evaporatorOutletStateChoice == "eta"')
	dTOutletEvaporator = Quantity('TemperatureDifference', default = (5, 'degC'), minValue = 1e-3, maxValue = 1e10, label = 'outlet subcooling', show = 'self.evaporatorOutletStateChoice == "dT"')
	qOutletEvaporator = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'outlet vapor quality', show = 'self.evaporatorOutletStateChoice == "Q"')
	TOutletEvaporator = Quantity('Temperature', default = (-10, 'degC'), label = 'outlet temperature', show = 'self.evaporatorOutletStateChoice == "T"')
	hOutletEvaporator = Quantity('SpecificEnthalpy', default = (100, 'kJ/kg'), minValue = -1e10, label = 'outlet enthalpy', show = 'self.evaporatorOutletStateChoice == "H"')

	evaporatorInputs = FieldGroup([TEvaporation, evaporatorOutletStateChoice, etaEvaporator, TExtEvaporator, dTOutletEvaporator, 
			TOutletEvaporator, qOutletEvaporator, hOutletEvaporator], 
			label = 'Evaporator')

	
	inputs = SuperGroup([refrigerantInputs, compressorInputs, condenserInputs, evaporatorInputs])

	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)

	#--------------- Model view ---------------#
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)	

	#================ Results ================#
	#---------------- Fields ----------------#
	cycleStatesTable = TableView(label="Cycle states", dataLabels = ['T', 'p', 'rho', 'h', 'q', 's'], 
			quantities = ['Temperature', 'Pressure', 'Density', 'SpecificEnthalpy', 'VaporQuality', 'SpecificEntropy'],
 			options = {'formats': ['0.000', '0.000E0', '0.000', '0.000E0', '0.00', '0.000E0']})

	cycleStates = ViewGroup([cycleStatesTable], label = "States")
	resultValues = SuperGroup([cycleStates], label="Values")
	#---------------- Cycle diagram -----------#
	diagram = Image(default='', width=880, height=550)
	diagramViewGroup = ViewGroup([diagram], label = "P-H Diagram")
	resultDiagrams = SuperGroup([diagramViewGroup], label = "Diagrams")

	#--------------- Model view ---------------#
	resultView = ModelView(ioType = "output", superGroups = [resultValues, resultDiagrams])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#
	def compute(self):
		cycleStateTableDType = np.dtype([
			('T', np.float), ('p', np.float), ('rho', np.float), 
			('h', np.float), ('q', np.float), ('s', np.float)
			])
		self.cycleStatesTable = np.zeros((4,), dtype = cycleStateTableDType)

		cycle = ReverseBraytonCycle(self.fluidName,
				compressor = CompressorOneStage(self.compressorModelType, self.etaCompressor, self.fQCompressor),
				condenser = IsobaricHeatExchanger(),
				evaporator = IsobaricHeatExchanger()
		)

		cycle.setTEvaporation(self.TEvaporation)
		cycle.setTCondensation(self.TCondensation)
		
		cycle.evaporator.compute(
			self.evaporatorOutletStateChoice, pIn = cycle.pLow,
			eta = self.etaEvaporator, TExt = self.TExtEvaporator, 
			dT = self.dTOutletEvaporator, q = self.qOutletEvaporator, 
			T = self.TOutletEvaporator, h = self.hOutletEvaporator)
		
		cycle.compressor.compute(cycle.pHigh)

		cycle.condenser.compute(self.condenserOutletStateChoice,
			eta = self.etaCondenser, TExt = self.TExtCondenser, 
			dT = self.dTOutletCondenser, q = self.qOutletCondenser, 
			T = self.TOutletCondenser, h = self.hOutletCondenser)
	
		cycle.throttleValve.compute(cycle.pLow)

		for i in range(len(cycle.fp)):
			fp = cycle.fp[i]
			self.cycleStatesTable[i] = (fp.T, fp.p, fp.rho, fp.h, fp.q, fp.s)

		self.createStateDiagram(cycle)

	def createStateDiagram(self, cycle):
		diagram = PHDiagram(self.fluidName, temperatureUnit = 'degC')
		diagram.setLimits()
		fig  = diagram.draw()
		ax = fig.get_axes()[0]
		
		ncp = len(cycle.fp)
		for i in range(ncp):
			ax.semilogy(cycle.fp[i].h/1e3, cycle.fp[i].p/1e5, 'ko')
			ax.semilogy(
				[cycle.fp[i].h/1e3, cycle.fp[(i + 1)%ncp].h/1e3], 
				[cycle.fp[i].p/1e5, cycle.fp[(i + 1)%ncp].p/1e5],
				'k', linewidth = 2)
			ax.annotate('{}'.format(i+1), 
				xy = (cycle.fp[i].h/1e3, cycle.fp[i].p/1e5),
				xytext = (10, 3), textcoords = 'offset points',
				size = 'x-large')
		fHandle, resourcePath  = diagram.export(fig)
		self.diagram = resourcePath
		os.close(fHandle)

		
		
class HeatPumpDoc(RestModule):
	name = 'HeatPumpDoc'
	label = 'Heat Pump (Docs)'
	template = 'documentation/html/HeatPumpDoc.html'
		
if __name__ == '__main__':
	#IsentropicCompression.test()
	pass