'''
Created on Nov 09, 2014
@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from lib.CycleBases import HeatPumpCycle

class VaporCompressionCycle(HeatPumpCycle):
	label = "Vapor compression cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/VaporCompressionCycle.svg")
	description = F.ModelDescription("Basic vapor compression cycle used in refrigerators and air conditioners", show = True)

	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	compressor = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Compressor')
	condenser = F.SubModelGroup(TC.Condenser, 'FG', label = 'Condenser')
	throttleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', label = 'JT valve')
	evaporator = F.SubModelGroup(TC.Evaporator, 'FG', label = 'Evaporator')
	inputs = F.SuperGroup(['workingFluidGroup', compressor, condenser, evaporator], label = 'Cycle definition')

	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	exampleAction = ServerAction("loadEg", label = "Examples", options = (
			('R134aCycle', 'Typical fridge with R134a as a refrigerant'),
			('CO2TranscriticalCycle', 'CO2 transcritial cycle'),
	))
	inputActionBar = ActionBar([computeAction, exampleAction], save = True)
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs, 'cycleDiagram'], 
		actionBar = inputActionBar, autoFetch = True)	

	#================ Results ================#
	compressorPower = F.Quantity('Power', default = (1, 'kW'), label = 'compressor power')
	condenserHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'condenser heat out')
	evaporatorHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'evaporator heat in')
	flowFieldGroup = F.FieldGroup([compressorPower, condenserHeat, evaporatorHeat], label = 'Energy flows')
	resultEnergy = F.SuperGroup([flowFieldGroup, 'efficiencyFieldGroup'], label = 'Energy')
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', resultEnergy])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#
	def __init__(self):
		self.R134aCycle()
		
	def compute(self):
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')
		if (self.cycleSupercritical and self.evaporator.computeMethod == 'dT'):
			raise ValueError('In supercritical cycle, evaporator super-heating cannot be used as input')
		self.initCompute(fluid = self.fluidName)
		# Connect components
		self.connectPorts(self.evaporator.outlet, self.compressor.inlet)
		self.connectPorts(self.compressor.outlet, self.condenser.inlet)
		self.connectPorts(self.condenser.outlet, self.throttleValve.inlet)
		self.connectPorts(self.throttleValve.outlet, self.evaporator.inlet)
		# Initial guess
		self.evaporator.outlet.state.update_pq(self.pLow, 1)
		# Cycle iterations
		self.cycleIterator.run()
		# Results
		self.postProcess()
	
	def computeCycle(self):
		self.compressor.compute(self.pHigh)
		self.condenser.compute()
		self.throttleValve.compute(self.pLow)
		self.evaporator.compute()
		
		
	def postProcess(self):
		super(VaporCompressionCycle, self).postProcess(self.TAmbient)
		# Flows
		self.compressorPower = self.mDot * self.compressor.w
		self.compressorHeat = -self.mDot * self.compressor.qIn
		self.condenserHeat = -self.mDot * self.condenser.qIn
		self.evaporatorHeat = self.mDot * self.evaporator.qIn
		# Efficiencies
		self.COPCooling = self.evaporatorHeat / self.compressorPower
		self.COPHeating = self.condenserHeat / self.compressorPower


	def CO2TranscriticalCycle(self):
		self.fluidName = 'CarbonDioxide'
		self.pHighMethod = 'P'
		self.pHigh = (130, 'bar')
		self.pLowMethod = 'T'
		self.TEvaporation = (10, 'degC')
		self.compressor.eta = 0.8
		self.compressor.fQ = 0.2
		self.condenser.computeMethod = 'T'
		self.condenser.TOutlet = (50, 'degC')
		self.evaporator.computeMethod = 'dT'
		self.evaporator.dTOutlet = (5, 'degC')
	
	def R134aCycle(self):
		self.fluidName = 'R134a'
		self.pHighMethod = 'P'
		self.pHigh = (10, 'bar')
		self.pLowMethod = 'T'
		self.TEvaporation = (-20, 'degC')
		self.compressor.eta = 0.75
		self.compressor.fQ = 0.0
		self.condenser.computeMethod = 'T'
		self.condenser.TOutlet = (36, 'degC')
		self.evaporator.computeMethod = 'Q'
		self.evaporator.qOutlet = 1.0

class VaporCompressionCycleWithRecuperator(VaporCompressionCycle):
	label = "Vapor compression cycle (recuperator)"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/VaporCompressionCycle_Recuperator.svg")
	description = F.ModelDescription("Vapor compression cycle with a recuperator. The stream \
	 before the throttle valve is precooled, using the cold stream at the evaporator outlet. \
	 This increases the compressor cooling/heating capacity of the cycle and improves slightly the COP", show = True)
	#================ Inputs ================#
	#---------------- Fields ----------------#
	recuperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator')
	inputs = F.SuperGroup(['workingFluidGroup', 'compressor', recuperator, 'condenser', 'evaporator'], label = 'Cycle definition')
	#--------------- Model view ---------------#

	#================ Results ================#
	#---------------- Energy flows -----------#
	recuperatorHeat = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'recuperator heat rate')
	flowFieldGroup = F.FieldGroup(['compressorPower', recuperatorHeat, 'condenserHeat', 'evaporatorHeat'], label = 'Energy flows')
	#================ Methods ================#
	def compute(self):
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')
		self.initCompute(fluid = self.fluidName)
		# Connect components
		self.connectPorts(self.evaporator.outlet, self.recuperator.inlet1)
		self.connectPorts(self.recuperator.outlet1, self.compressor.inlet)
		self.connectPorts(self.compressor.outlet, self.condenser.inlet)
		self.connectPorts(self.condenser.outlet, self.recuperator.inlet2)
		self.connectPorts(self.recuperator.outlet2, self.throttleValve.inlet)
		self.connectPorts(self.throttleValve.outlet, self.evaporator.inlet)
		# Initial guess
		self.evaporator.outlet.state.update_pq(self.pLow, 1)
		if (self.cycleTranscritical):
			self.condenser.outlet.state.update_Tp(1.05 * self.fluid.critical['T'], self.pHigh)
		else:
			self.condenser.outlet.state.update_pq(self.pHigh, 0)
		# Cycle iterations
		self.cycleIterator.run()
		# Results
		self.postProcess()
	
	def computeCycle(self):
		self.recuperator.compute(self.mDot, self.mDot)
		self.recuperator.computeStream1(self.mDot)
		self.compressor.compute(self.pHigh)
		self.condenser.compute()
		self.recuperator.computeStream2(self.mDot)
		self.throttleValve.compute(self.pLow)
		self.evaporator.compute()
		
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')
	
	def postProcess(self):
		super(VaporCompressionCycleWithRecuperator, self).postProcess()
		self.recuperatorHeat = self.recuperator.QDot
	
	def R134aCycle(self):
		super(VaporCompressionCycleWithRecuperator, self).R134aCycle()
		self.recuperator.eta = 0.7
