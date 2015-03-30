'''
Created on Mar 20, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from lib.CycleBases import HeatEngineCycle

class RankineCycle(HeatEngineCycle):
	label = "Rankine cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/RankineCycle.png",  height = 300)
	description = F.ModelDescription("Basic Rankine cycle used in power generation", show = True)
	
	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	pump = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Pump')
	boiler = F.SubModelGroup(TC.Evaporator, 'FG', label = 'Boiler')
	turbine = F.SubModelGroup(TC.Turbine, 'FG', label = 'Turbine')
	condenser = F.SubModelGroup(TC.Condenser, 'FG', label = 'Condenser')
	inputs = F.SuperGroup(['workingFluidGroup', pump, boiler, turbine, condenser], label = 'Cycle definition')	
	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	exampleAction = ServerAction("loadEg", label = "Examples", options = (
			('SteamPlant', 'Typical steam power plant'),
			('ORC1', 'Geothermal Organic Rankine Cycle with R134a'),
	))
	inputActionBar = ActionBar([computeAction, exampleAction], save = True)
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs, 'cycleDiagram', 'solver'], 
		actionBar = inputActionBar, autoFetch = True)
	#================ Results ================#
	#---------------- Energy flows -----------#
	pumpPower = F.Quantity('Power', default = (1, 'kW'), label = 'pump power')
	boilerHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'boiler heat in')
	turbinePower = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'turbine power')
	condenserHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'condenser heat out')
	flowFieldGroup = F.FieldGroup([pumpPower, boilerHeat, turbinePower, condenserHeat], label = 'Energy flows')
	resultEnergy = F.SuperGroup([flowFieldGroup, 'efficiencyFieldGroup'], label = 'Energy')
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', resultEnergy, 'solverStats'])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#
	def __init__(self):
		self.SteamPlant()
		
	def compute(self):
		if (self.cycleTranscritical and 
				(self.boiler.computeMethod == 'dT' or self.boiler.computeMethod == 'Q')):
			raise ValueError('In transcritical cycle, boiler super-heating cannot be used as input')
		if (self.cycleSupercritical and 
				(self.condenser.computeMethod == 'dT' or self.condenser.computeMethod == 'Q')):
			raise ValueError('In supercritical cycle condenser sub-cooling cannot be used as input')
		# Connect components to points
		self.initCompute(self.fluidName)
		self.connectPorts(self.condenser.outlet, self.pump.inlet)
		self.connectPorts(self.pump.outlet, self.boiler.inlet)
		self.connectPorts(self.boiler.outlet, self.turbine.inlet)
		self.connectPorts(self.turbine.outlet, self.condenser.inlet)
		# Initial guess
		for fl in self.flows:
			fl.mDot = self.mDot
		self.condenser.outlet.state.update_pq(self.pLow, 0)
		# Cycle iterations
		self.solver.run()
		# Results
		self.postProcess()
		
	def computeCycle(self):
		self.pump.compute(self.pHigh)
		self.boiler.compute()	
		self.turbine.compute(self.pLow)
		self.condenser.compute()
		
	def postProcess(self):
		super(RankineCycle, self).postProcess(self.TAmbient)
		# Flows
		self.pumpPower = self.mDot * self.pump.w 
		self.boilerHeat = self.mDot * self.boiler.qIn
		self.turbinePower = - self.mDot * self.turbine.w
		self.condenserHeat = - self.mDot * self.condenser.qIn 
		# Efficiencies
		self.eta = (self.turbinePower - self.pumpPower) / self.boilerHeat
		self.etaCarnot = 1 - self.condenser.outlet.state.T / self.boiler.outlet.state.T
		self.etaSecondLaw = self.eta / self.etaCarnot
	
	def SteamPlant(self):
		self.fluidName = 'Water'
		self.mDot = 25.
		self.pHighMethod = 'P'
		self.pHigh = (35, 'bar')
		self.pLowMethod = 'P'
		self.pLow = (0.5, 'bar')
		self.boiler.computeMethod = 'T'
		self.boiler.TOutlet = (400, 'degC')
		self.turbine.eta = 0.85
		self.condenser.computeMethod = 'Q'
		self.condenser.qOutlet = 0
	
	def ORC1(self):
		self.fluidName = 'R134a'
		self.mDot = (10, 'kg/min')
		self.pHighMethod = 'T'
		self.TEvaporation = (85, 'degC')
		self.pLowMethod = 'T'
		self.TCondensation = (40, 'degC')
		self.boiler.computeMethod = 'Q'
		self.boiler.qOutlet = 1
		self.turbine.eta = 0.8
		self.condenser.computeMethod = 'Q'
		self.condenser.qOutlet = 0

class RegenerativeRankineCycle(RankineCycle):
	label = "Regenerative Rankine cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/RankineCycle_Recuperator.svg",  height = 300)
	description = F.ModelDescription("Rankine cycle with recuperator, \
		using the temperature of the hot steam before the condenser to pre-heat the fluid before entering the boiler", show = True)
	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	recuperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator')
	inputs = F.SuperGroup(['workingFluidGroup', 'pump', recuperator, 'boiler', 'turbine', 'condenser'], label = 'Cycle defininition')
	#--------------- Model view ---------------#

	#================ Results ================#
	#---------------- Energy flows -----------#
	recuperatorHeat = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'recuperator heat rate')
	flowFieldGroup = F.FieldGroup(['pumpPower', recuperatorHeat, 'boilerHeat', 'turbinePower', 'condenserHeat'], label = 'Energy flows')
	#================ Methods ================#
	def compute(self):
		self.initCompute(self.fluidName)
		# Connect components
		self.connectPorts(self.condenser.outlet, self.pump.inlet)
		self.connectPorts(self.pump.outlet, self.recuperator.inlet1)
		self.connectPorts(self.recuperator.outlet1, self.boiler.inlet)
		self.connectPorts(self.boiler.outlet, self.turbine.inlet)
		self.connectPorts(self.turbine.outlet, self.recuperator.inlet2)
		self.connectPorts(self.recuperator.outlet2, self.condenser.inlet)
		# Initial guess
		for fl in self.flows:
			fl.mDot = self.mDot
		self.condenser.outlet.state.update_pq(self.pLow, 0)
		self.boiler.outlet.state.update_pq(self.pHigh, 1)
		self.turbine.compute(self.pLow)
		# Cycle iterations
		self.solver.run()
		# Results
		self.postProcess()
		
	def computeCycle(self):
		self.pump.compute(self.pHigh)
		self.recuperator.compute()
		self.recuperator.computeStream1()
		self.boiler.compute()	
		self.turbine.compute(self.pLow)
		self.recuperator.computeStream2()
		self.condenser.compute()
		
	def postProcess(self):
		super(RegenerativeRankineCycle, self).postProcess()
		self.recuperatorHeat = self.recuperator.QDot 

	def SteamPlant(self):
		RankineCycle.SteamPlant(self)
		self.pLow = (2, 'bar')
		self.boiler.TOutlet = (600, 'degC')
