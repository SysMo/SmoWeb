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
	inletJunct = F.SubModelGroup(TC.FlowJunction, 'FG')
	compressor = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Compressor')
	cooler = F.SubModelGroup(TC.Condenser, 'FG', label = 'Cooler')
	recuperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator')
	throttleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', label = 'JT valve')
	liqSeparator = F.SubModelGroup(TC.PhaseSeparator, 'FG', label = 'Liquid separator')
	secThrottleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', label = 'JT valve')
	liquidSink = F.SubModelGroup(TC.FluidSink, 'FG')
	inputs = F.SuperGroup(['workingFluidGroup', compressor, cooler, recuperator], label = 'Cycle definition')

	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	exampleAction = ServerAction("loadEg", label = "Examples", options = (
			('ArgonLiquefaction', 'Argon liquefaction cycle'),
			('NitrogenLiquefaction', 'Nitrogen liquefacton cycle'),
	))
	inputActionBar = ActionBar([computeAction, exampleAction], save = True)
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs, 'cycleDiagram', 'solver'], 
		actionBar = inputActionBar, autoFetch = True)	

	#================ Results ================#
	compressorPower = F.Quantity('Power', default = (1, 'kW'), label = 'compressor power')
	compressorHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'compressor heat')
	coolerHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'cooler heat out')
	flowFieldGroup = F.FieldGroup([compressorPower, compressorHeat, coolerHeat], label = 'Flows')
	resultEnergy = F.SuperGroup([flowFieldGroup, 'efficiencyFieldGroup'], label = 'Energy')
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', resultEnergy, 'solverStats'])

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
		self.connectPorts(self.liqSeparator.outletLiquid, self.liquidSink.inlet)
		# Initialize source
		self.gasSource.T = self.TIn
		self.gasSource.p = self.pIn
		self.gasSource.mDot = self.mDot
		self.gasSource.compute()
		# Initial guess
		liqFractionGuess = 0.2
		self.compressor.inlet.flow.mDot = 1.0 / liqFractionGuess * self.gasSource.outlet.flow.mDot
		self.liqSeparator.outletVapor.flow.mDot = liqFractionGuess * self.mDot

		self.compressor.inlet.state.update_Tp(
			self.gasSource.outlet.state.T, self.gasSource.outlet.state.p)
		self.secThrottleValve.outlet.state.update_pq(self.pIn, 1)
		# Run solver
		self.solve()
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
		
	def createStateDiagram(self):
		lineNumbers = [(2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (6, 10), (7, 8), (8, 9)]
		fluidLines = []		
		for i, j in lineNumbers:
			fluidLines.append((self.fp[i - 1], self.fp[j - 1]))
		self.phDiagram = self.cycleDiagram.draw(self.fluid, self.fp, fluidLines)	

	def ArgonLiquefaction(self):
		self.fluidName = "Argon"
		self.pIn = (1, 'bar')
		self.TIn = 300
		self.pHigh = (200, 'bar')
		self.pLiquid = (1.2, 'bar')
		self.TAmbient = 300
		self.compressor.modelType = 'T'
		self.compressor.etaT = 0.8
		self.compressor.dT = 50.
		self.recuperator.eta = 0.99
		self.cycleDiagram.defaultMaxP = False
		self.cycleDiagram.maxPressure = (300, 'bar')
		
	def NitrogenLiquefaction(self):
		self.fluidName = "Nitrogen"
		self.pIn = (1, 'bar')
		self.TIn = 300
		self.pHigh = (300, 'bar')
		self.pLiquid = (1.2, 'bar')
		self.TAmbient = 300
		self.compressor.modelType = 'T'
		self.compressor.etaT = 0.8
		self.compressor.dT = 50.
		self.recuperator.eta = 0.99
		self.cycleDiagram.defaultMaxP = False
		self.cycleDiagram.defaultMaxT = False
		self.cycleDiagram.maxPressure = (500, 'bar')
		self.cycleDiagram.maxTemperature = 350
		
class ClaudeCycle(LindeHampsonCycle):
	label = "Claude cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/ClaudeCycle.svg",  height = 300)
	description = F.ModelDescription("Liquefaction cycle using 3 recurperators and an expander e.g. for air liquefaction", show = True)

	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	recuperator2 = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator 2')
	recuperator3 = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator 3')
	expander = F.SubModelGroup(TC.Turbine, 'FG', label = 'Expander')
	expanderFlowFraction = F.Quantity('Fraction', label = 'flow fraction')
	expanderEta = F.Quantity('Efficiency', label = 'efficiency')
	expanderFG = F.FieldGroup([expanderFlowFraction, expanderEta], label = 'Expander')
	expanderSplitter = F.SubModelGroup(TC.FlowSplitter, 'FG')
	expanderJunction = F.SubModelGroup(TC.FlowJunction, 'FG')
	inputs = F.SuperGroup(['workingFluidGroup', 'compressor', 'cooler', expanderFG, 'recuperator', recuperator2, recuperator3], label = 'Cycle definition')
	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	exampleAction = ServerAction("loadEg", label = "Examples", options = (
			('NitrogenMediumP', 'Nitrogen medium pressure (30 bar) liquefaction cycle'),
			('NitrogenLowP', 'Nitrogen low pressure (8 bar) liquefacton cycle'),
	))
	inputActionBar = ActionBar([computeAction, exampleAction], save = True)
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs, 'cycleDiagram', 'solver'], 
		actionBar = inputActionBar, autoFetch = True)
		
	def __init__(self):
		self.cooler.computeMethod = 'eta'
		self.cooler.TExt = self.TAmbient
		self.NitrogenMediumP()
		
	def compute(self):
		self.initCompute(self.fluidName)
		self.expanderSplitter.frac1 = 1 - self.expanderFlowFraction
		self.expanderSplitter.frac2 = self.expanderFlowFraction
		self.expander.eta = self.expanderEta
		# Connect components
		self.connectPorts(self.gasSource.outlet, self.inletJunct.inletMain)
		self.connectPorts(self.inletJunct.outlet, self.compressor.inlet)
		self.connectPorts(self.compressor.outlet, self.cooler.inlet)
		self.connectPorts(self.cooler.outlet, self.recuperator.inlet1)
		self.connectPorts(self.recuperator.outlet1, self.expanderSplitter.inlet)
		self.connectPorts(self.expanderSplitter.outlet1, self.recuperator2.inlet1)
		self.connectPorts(self.recuperator2.outlet1, self.recuperator3.inlet1)
		self.connectPorts(self.recuperator3.outlet1, self.throttleValve.inlet)
		self.connectPorts(self.throttleValve.outlet, self.liqSeparator.inlet)
		self.connectPorts(self.liqSeparator.outletVapor, self.secThrottleValve.inlet)
		self.connectPorts(self.secThrottleValve.outlet, self.recuperator3.inlet2)
		self.connectPorts(self.recuperator3.outlet2, self.expanderJunction.inletMain)
		self.connectPorts(self.expanderJunction.outlet, self.recuperator2.inlet2)
		self.connectPorts(self.recuperator2.outlet2, self.recuperator.inlet2)
		self.connectPorts(self.recuperator.outlet2, self.inletJunct.inlet2)
		self.connectPorts(self.expanderSplitter.outlet2, self.expander.inlet)
		self.connectPorts(self.expander.outlet, self.expanderJunction.inlet2)
		self.connectPorts(self.liqSeparator.outletLiquid, self.liquidSink.inlet)

		# Initial guess
		liqFractionGuess = 0.5
		for fl in self.flows:
			fl.mDot = 1.0 / liqFractionGuess * self.mDot
		for fp in self.fp:
			fp.update_Tp(self.TAmbient, self.pIn)
		
		
		# Initialize source
		self.gasSource.T = self.TIn
		self.gasSource.p = self.pIn
		self.gasSource.mDot = self.mDot
		self.gasSource.compute()
		# Run solver
		self.solve()
		# Results
		self.postProcess(self.TAmbient)
		
	def computeCycle(self):
		self.compressor.compute(self.pHigh)
		self.cooler.compute()
		self.recuperator.compute()
		self.recuperator.computeStream1()
		self.expanderSplitter.compute()
		self.recuperator2.compute()
		self.recuperator2.computeStream1()
		self.recuperator3.compute()
		self.recuperator3.computeStream1()
		self.throttleValve.compute(self.pLiquid)
		self.liqSeparator.compute()
		self.secThrottleValve.compute(self.pIn)
		self.recuperator3.computeStream2()
		self.expander.compute(self.pIn)
		self.expanderJunction.compute()
		self.recuperator2.computeStream2()
		self.recuperator.computeStream2()
		self.inletJunct.compute()

	def createStateDiagram(self):
		lineNumbers = [(2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9), (9, 10), (9, 18), (10, 11), (11, 12), (13, 14), (14, 15), (16, 17)]
		fluidLines = []		
		for i, j in lineNumbers:
			fluidLines.append((self.fp[i - 1], self.fp[j - 1]))
		self.phDiagram = self.cycleDiagram.draw(self.fluid, self.fp, fluidLines)	

	def NitrogenLiquefaction(self):
		self.fluidName = "Nitrogen"
		self.pIn = (1, 'bar')
		self.TIn = 300
		self.pHigh = (30, 'bar')
		self.pLiquid = (1.2, 'bar')
		self.TAmbient = 300
		self.compressor.modelType = 'T'
		self.compressor.etaT = 0.8
		self.compressor.dT = 50.
		self.cycleDiagram.defaultMaxP = False
		self.cycleDiagram.defaultMaxT = False
		self.cycleDiagram.maxPressure = (500, 'bar')
		self.cycleDiagram.maxTemperature = 350

	def NitrogenMediumP(self):
		self.fluidName = "Nitrogen"
		self.pIn = (1, 'bar')
		self.TIn = (300, 'K')
		self.mDot = (0.188, 'kg/s')
		self.pHigh = (30, 'bar')
		self.pLiquid = (1.2, 'bar')
		self.TAmbient = (300, 'K')
		self.compressor.modelType = 'T'
		self.compressor.etaT = 0.8
		self.compressor.dT = 50
		self.cooler.computeMethod = 'eta'
		self.cooler.etaThermal = 1.
		self.cooler.TExt = (30, 'degC')
		self.expanderEta = 0.8
		self.expanderFlowFraction = 0.66
		self.recuperator.computeMethod = 'EG'
		self.recuperator.epsGiven = 0.99
		self.recuperator2.computeMethod = 'EN'
		self.recuperator2.UA = (1950, 'W/K')
		self.recuperator3.computeMethod = 'EG'
		self.recuperator3.epsGiven = 0
		self.cycleDiagram.defaultMaxT = False
		self.cycleDiagram.maxTemperature = 400

	def NitrogenLowP(self):
		self.fluidName = "Nitrogen"
		self.pIn = (1.1, 'bar')
		self.TIn = (300, 'K')
		self.mDot = (12.8, 'kg/h')
		self.pHigh = (8, 'bar')
		self.pLiquid = (1.2, 'bar')
		self.TAmbient = (300, 'K')
		self.compressor.modelType = 'S'
		self.compressor.etaS = 0.8
		self.compressor.fQ = 0.3
		self.cooler.computeMethod = 'eta'
		self.cooler.etaThermal = 1.
		self.cooler.TExt = (310, 'K')
		self.expanderEta = 0.5
		self.expanderFlowFraction = 0.94
		self.recuperator.computeMethod = 'EN'
		self.recuperator.UA = (1280, 'W/K')
		self.recuperator2.computeMethod = 'EN'
		self.recuperator2.UA = (90, 'W/K')
		self.recuperator3.computeMethod = 'EG'
		self.recuperator3.epsGiven = 0
		self.cycleDiagram.defaultMaxT = False
		self.cycleDiagram.maxTemperature = 550
		