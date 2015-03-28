'''
Created on Mar 27, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from lib.CycleBases import LiquefactionCycle
import smo.web.exceptions as E
from smo.media.CoolProp.CoolProp import FluidState
from ThermoFluids.models.lib.Ports import FluidFlow

class LindeHampsonCycle(LiquefactionCycle):
	label = "Linde-Hampson cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/LindeHampson.svg",  height = 300)
	description = F.ModelDescription("Basic liquefaction cycle used e.g. for air liquefaction", show = True)

	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	gasSource = F.SubModelGroup(TC.FluidSource_TP, 'FG')
	inletJunct = F.SubModelGroup(TC.FluidJunction, 'FG')
	compressor = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Compressor')
	cooler = F.SubModelGroup(TC.Condenser, 'FG', label = 'Cooler')
	recuperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator')
	throttleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', label = 'JT valve')
	liqSeparator = F.SubModelGroup(TC.PhaseSeparator, 'FG', label = 'Liquid separator')
	secThrottleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', label = 'JT valve')
	inputs = F.SuperGroup(['workingFluidGroup', compressor, cooler, recuperator], label = 'Cycle definition')

	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	exampleAction = ServerAction("loadEg", label = "Examples", options = (
			('ArgonLiquefaction', 'Argon liquefaction cycle'),
			('NitrogenLiquefaction', 'Nitrogen liquefacton cycle'),
	))
	inputActionBar = ActionBar([computeAction, exampleAction], save = True)
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs, 'cycleDiagram'], 
		actionBar = inputActionBar, autoFetch = True)	

	#================ Results ================#
	compressorPower = F.Quantity('Power', default = (1, 'kW'), label = 'compressor power')
	compressorHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'compressor heat')
	coolerHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'cooler heat out')
	flowFieldGroup = F.FieldGroup([compressorPower, compressorHeat, coolerHeat], label = 'Flows')
	resultEnergy = F.SuperGroup([flowFieldGroup, 'efficiencyFieldGroup'], label = 'Energy')
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', resultEnergy])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#
	def __init__(self):
		self.cooler.computeMethod = 'eta'
		self.cooler.TExt = self.TAmbient
		self.ArgonLiquefaction()
		
	def compute(self):
		self.initCompute(self.fluidName)
		# Connect components
		self.connectPorts(self.gasSource.outlet, self.inletJunct.inletMain)
		self.connectPorts(self.inletJunct.outlet, self.compressor.inlet)
		self.connectPorts(self.compressor.outlet, self.cooler.inlet)
		self.connectPorts(self.cooler.outlet, self.recuperator.inlet1)
		self.connectPorts(self.recuperator.outlet1, self.throttleValve.inlet)
		self.connectPorts(self.throttleValve.outlet, self.liqSeparator.inlet)
		self.connectPorts(self.liqSeparator.outletVapor, self.secThrottleValve.inlet)
		self.connectPorts(self.secThrottleValve.outlet, self.recuperator.inlet2)
		self.connectPorts(self.recuperator.outlet2, self.inletJunct.inlet2)
		self.liqSeparator.outletLiquid.state = FluidState(self.fluidName)
		self.liqSeparator.outletLiquid.flow = FluidFlow()
		# Initialize source
		self.gasSource.T = self.TIn
		self.gasSource.p = self.pIn
		self.gasSource.mDot = self.mDot
		self.gasSource.compute()
		# Initial guess
		self.compressor.inlet.state.update_Tp(
			self.gasSource.outlet.state.T, self.gasSource.outlet.state.p)
		self.compressor.inlet.flow.mDot = 1.0 * self.gasSource.outlet.flow.mDot
		self.secThrottleValve.outlet.state.update_pq(self.pIn, 1)
		self.liqSeparator.outletVapor.flow.mDot = 0.5 * self.mDot
		# Cycle iterations
		self.cycleIterator.run()
		# Results
		self.postProcess(self.TAmbient)
		
	def computeCycle(self):
		self.compressor.compute(self.pHigh)
		self.cooler.compute()
		self.recuperator.compute()
		self.recuperator.computeStream1()
		self.throttleValve.compute(self.pLiquid)
		self.liqSeparator.compute()
		self.secThrottleValve.compute(self.pIn)
		self.recuperator.computeStream2()
		self.inletJunct.compute()
		
	def postProcess(self, TAmbient):
		LiquefactionCycle.postProcess(self, TAmbient)
		self.compressor.postProcess()
		self.cooler.postProcess()
		# Flows
		self.compressorPower = self.compressor.WDot
		self.compressorHeat = - self.compressor.QDotIn
		self.coolerHeat = - self.cooler.QDotIn
		# Efficiencies
		self.liqEnergy = self.compressor.WDot / self.liqSeparator.outletLiquid.flow.mDot
		self.minLiqEnergy = self.liqSeparator.outletLiquid.state.b(self.TAmbient) \
			- self.gasSource.outlet.state.b(self.TAmbient)
		self.etaSecondLaw = self.minLiqEnergy / self.liqEnergy
		
	def ArgonLiquefaction(self):
		self.fluidName = "Argon"
		self.pIn = (1, 'bar')
		self.TIn = 300
		self.pHigh = (200, 'bar')
		self.pLiquid = (1, 'bar')
		self.TAmbient = 300
		self.compressor.modelType = 'T'
		self.recuperator.eta = 1.0
		self.cycleDiagram.defaultMaxP = False
		self.cycleDiagram.maxPressure = (300, 'bar')
		
	def NitrogenLiquefaction(self):
		self.fluidName = "Nitrogen"
		self.pIn = (1, 'bar')
		self.TIn = 300
		self.pHigh = (300, 'bar')
		self.pLiquid = (1, 'bar')
		self.TAmbient = 300
		self.compressor.modelType = 'T'
		self.recuperator.eta = 1.0
		self.cycleDiagram.defaultMaxP = False
		self.cycleDiagram.defaultMaxT = False
		self.cycleDiagram.maxPressure = (500, 'bar')
		self.cycleDiagram.maxTemperature = 350		