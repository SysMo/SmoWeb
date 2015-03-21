'''
Created on Nov 09, 2014
@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.media.MaterialData import Fluids

from smo.media.calculators.processes import ReverseBraytonCycle1, CompressorOneStage, IsobaricHeatExchanger,\
	ThermodynamicCycle
from smo.media.diagrams.StateDiagrams import PHDiagram
class ReverseBraytonCycle(NumericalModel):
	label = "Reverse Brayton cycle"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/ReverseBraytonCycle.svg")
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
		('dT', 'sub-cooling'),
		('Q', 'vapor quality'),
		('eta', 'thermal efficiency'),
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
		('dT', 'super-heating'),
		('Q', 'vapor quality'),
		('eta', 'thermal efficiency'),
		('T', 'temperature'),
		('H', 'enthalpy'),
	)), label = 'compute outlet by')
	etaEvaporator = Quantity(default = 0.9, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.evaporatorOutletStateChoice == "eta"')
	TExtEvaporator = Quantity('Temperature', default = (0, 'degC'), label = 'external temperature', show = 'self.evaporatorOutletStateChoice == "eta"')
	dTOutletEvaporator = Quantity('TemperatureDifference', default = (5, 'degC'), minValue = 1e-3, maxValue = 1e10, label = 'outlet superheating', show = 'self.evaporatorOutletStateChoice == "dT"')
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
	cycleStatesTable = TableView((
		('T', Quantity('Temperature', default = (1, 'K'))),
		('p', Quantity('Pressure', default = (1, 'bar'))),
		('rho', Quantity('Density', default = (1, 'kg/m**3'))),
		('h', Quantity('SpecificEnthalpy', default = (1, 'kJ/kg'))),
		('s', Quantity('SpecificEntropy', default = (1, 'kJ/kg-K'))),
		('q', Quantity()),
		), label="Cycle states")
						
	cycleStates = ViewGroup([cycleStatesTable], label = "States")
	resultStates = SuperGroup([cycleStates], label="States")
	#---------------- Cycle diagram -----------#
	diagram = Image(default='', width=880, height=550)
	diagramViewGroup = ViewGroup([diagram], label = "P-H Diagram")
	resultDiagrams = SuperGroup([diagramViewGroup], label = "Diagrams")
	#---------------- Work/heat/mass flows -----------#
	compressorWork = Quantity('Power', default = (1, 'kW'), label = 'Compressor work')
	compressorHeat = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'Compressor heat out')
	condenserHeat = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'Condenser heat out')
	evaporatorHeat = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'Evaporator heat in')
	flowFieldGroup = FieldGroup([compressorWork, compressorHeat, condenserHeat, evaporatorHeat], label = 'Energy flows')
	COPCooling = Quantity(label = 'COP cooling', description = 'COP when working in cooling mode')
	COPHeating = Quantity(label = 'COP heating', description = 'COP when working in heating mode')
	COPCarnotCooling = Quantity(label = 'COP Carnot cooling', description = 'COP (cooling) of Carnot cycle between the high (condenser) temperature and the low (evaporator) tempreature')
	COPCarnotHeating = Quantity(label = 'COP Carnot heating', description = 'COP (heating) of Carnot cycle between the high (condenser) temperature and the low (evaporator) tempreature')
	efficiencyFieldGroup = FieldGroup([COPCooling, COPHeating, COPCarnotCooling, COPCarnotHeating], 'Efficiency')
# 	flowTable = TableView((
# 		('Component', String(maxLength = 20)),
# 		('Flow rate', Quantity('MassFlowRate', default = (1, 'kg/min'))),
# 		('Heat rate in', Quantity('HeatFlowRate', default = (1, 'kW'))),
# 		('Work in', Quantity('Power', default = (1, 'kW'))),		
# 	))
	resultFlows = SuperGroup([flowFieldGroup, efficiencyFieldGroup], label = 'Energy')
	#--------------- Model view ---------------#
	resultView = ModelView(ioType = "output", superGroups = [resultDiagrams, resultStates, resultFlows])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#
	def compute(self):
		#ThermodynamicCycle.__init__(self, fluid = self.fluidName, numPoints = 4)

		cycle = ReverseBraytonCycle1(self.fluidName,
				compressor = CompressorOneStage(self.compressorModelType, self.etaCompressor, self.fQCompressor),
				condenser = IsobaricHeatExchanger(),
				evaporator = IsobaricHeatExchanger()
		)

		cycle.setTEvaporation(self.TEvaporation)
		cycle.setTCondensation(self.TCondensation)
		
		cycle.fp[0].update_pq(cycle.pLow, 1)
		absToleranceEnthalpy = 1.0;
		numIter = 20
		i = 0
		while (i < numIter):
			hOld = cycle.fp[0].h
			self.computeCycle(cycle)
			hNew = cycle.fp[0].h
			print (hNew)
			if (abs(hOld - hNew) < absToleranceEnthalpy):
				break
		if (hOld - hNew >= absToleranceEnthalpy):
			raise ConvergenceError('Solution did not converge')
		# Results
		## State diagram
		self.createStateDiagram(cycle)
		## Table of states
		self.cycleStatesTable.resize(4)
		for i in range(len(cycle.fp)):
			fp = cycle.fp[i]
			self.cycleStatesTable[i] = (fp.T, fp.p, fp.rho, fp.h, fp.s, fp.q)

		self.compressorWork = self.mDotRefrigerant * cycle.compressor.w
		self.compressorHeat = -self.mDotRefrigerant * cycle.compressor.qIn
		self.condenserHeat = -self.mDotRefrigerant * cycle.condenser.qIn
		self.evaporatorHeat = self.mDotRefrigerant * cycle.evaporator.qIn
		self.COPCooling = self.evaporatorHeat / self.compressorWork
		self.COPHeating = self.condenserHeat / self.compressorWork
		self.COPCarnotCooling = cycle.TEvaporation / (cycle.TCondensation - cycle.TEvaporation)
		self.COPCarnotHeating = cycle.TCondensation / (cycle.TCondensation - cycle.TEvaporation)
		## Table of flows
# 		self.flowTable.resize(4)
# 		i = 0
# 		for component in cycle.components:
# 			mDot = self.mDotRefrigerant
# 			self.flowTable[i] = (component.name, self.mDotRefrigerant, mDot * component.qIn, mDot * component.w)
# 			i += 1
# 		print self.flowTable
	
	
	def computeCycle(self, cycle):
		cycle.compressor.compute(cycle.pHigh)

		cycle.condenser.compute(self.condenserOutletStateChoice,
			eta = self.etaCondenser, TExt = self.TExtCondenser, 
			dT = self.dTOutletCondenser, q = self.qOutletCondenser, 
			T = self.TOutletCondenser, h = self.hOutletCondenser)
	
		cycle.throttleValve.compute(cycle.pLow)

		cycle.evaporator.compute(
			self.evaporatorOutletStateChoice,
			eta = self.etaEvaporator, TExt = self.TExtEvaporator, 
			dT = self.dTOutletEvaporator, q = self.qOutletEvaporator, 
			T = self.TOutletEvaporator, h = self.hOutletEvaporator)

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