import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from collections import OrderedDict
from lib.CycleBases import ThermodynamicalCycle
from smo.media.CoolProp.CoolProp import Fluid

class ThermodynamicalProcess(ThermodynamicalCycle):
	############# Inputs #############
	fluidSource = F.SubModelGroup(TC.FluidSource, 'FG', label = 'Initial State')
	fluidSink = F.SubModelGroup(TC.FluidSink, 'FG', label = 'Final State')
	inputs = F.SuperGroup([fluidSource, fluidSink])
	
	# Model View
	inputView = F.ModelView(ioType = "input", superGroups = [inputs], autoFetch = True)
	
	############# Results #############
	w = F.Quantity('SpecificEnergy', default = (0, 'kJ/kg'), label = 'specific work')
	qIn = F.Quantity('SpecificEnergy', default = (0, 'kJ/kg'), label = 'specific heat in')
	delta_h = F.Quantity('SpecificEnthalpy', label = 'enthalpy change (fluid)')
	WDot = F.Quantity('Power', default = (0, 'kW'), label = 'power')
	QDotIn = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'heat flow rate in')
	deltaHDot = F.Quantity('Power', label = 'enthalpy change (fluid)') 
	# Specific energy quantities
	specificEnergyResults = F.FieldGroup([w, delta_h, qIn], label = "Heat/work (specific quantities)")
	# Energy flow quantities
	energyFlowResults = F.FieldGroup([WDot, deltaHDot, QDotIn], label = "Heat/work flows")
	energyBalanceResults = F.SuperGroup([specificEnergyResults, energyFlowResults], label = "Energy balance")
	
	# Model View
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', energyBalanceResults])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	############# Methods ###############
	def postProcess(self, component):
		super(ThermodynamicalProcess, self).postProcess(300)
		component.postProcess()
		self.w = component.w
		self.qIn = component.qIn
		self.delta_h = component.delta_h
		self.WDot = component.WDot
		self.QDotIn = component.QDotIn
		self.deltaHDot = component.deltaHDot	

class Compression(ThermodynamicalProcess):
	label = "Compression"
	description = F.ModelDescription("Parameteric model for compression process: isentropic and isothermal", show = True)
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/Compression.svg")	
	compressor = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Compressor')
	inputs = F.SuperGroup(['fluidSource', 'fluidSink', compressor])
	
	def compute(self):
		self.initCompute(self.fluidSource.fluidName)
		# Connect components
		self.connectPorts(self.fluidSource.outlet, self.compressor.inlet)
		self.connectPorts(self.compressor.outlet, self.fluidSink.inlet)
		self.fluidSource.compute()
		self.compressor.compute(self.fluidSink.p)	
		self.postProcess(self.compressor)
		
class Expansion(ThermodynamicalProcess):
	label = "Expansion"
	description = F.ModelDescription("Parameteric model for expansion process: isentropic and isenthalpic", show = True)
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/Expansion.svg")
	turbine = F.SubModelGroup(TC.Turbine, 'FG', label = 'Turbine', show="self.processType == 'S'")
	throttleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', show="false")
	processType = F.Choices(options = OrderedDict((
														('S', 'isentropic'),
														('H', 'isenthalpic'),
													)), default = 'S', label = "process type")
	processTypeFG = F.FieldGroup([processType], label = "Process type")
	inputs = F.SuperGroup(['fluidSource', 'fluidSink', processTypeFG, turbine, throttleValve])
	
	def __init__(self):
		self.fluidSource.p1 = (10, 'bar')
		self.fluidSource.p2 = (10, 'bar')
		self.fluidSink.p = (1, 'bar')
		
	
	def compute(self):
		if (self.processType == 'S'):
			component = self.turbine
		elif (self.processType == 'H'):
			component = self.throttleValve
		self.initCompute(self.fluidSource.fluidName)
		# Connect components
		self.connectPorts(self.fluidSource.outlet, component.inlet)
		self.connectPorts(component.outlet, self.fluidSink.inlet)
		self.fluidSource.compute()
		component.compute(self.fluidSink.p)	
		self.postProcess(component)

class Heating(ThermodynamicalProcess):
	label = "Heating"
	description = F.ModelDescription("Heating process at constant pressure", show = True)
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/Heating.svg")
	evaporator = F.SubModelGroup(TC.Evaporator, 'FG', label = 'Evaporator')
	inputs = F.SuperGroup(['fluidSource', evaporator])

	############# Methods ###############
	def compute(self):
		self.initCompute(self.fluidSource.fluidName)
		# Connect components
		self.connectPorts(self.fluidSource.outlet, self.evaporator.inlet)
		self.connectPorts(self.evaporator.outlet, self.fluidSink.inlet)
		self.fluidSource.compute()
		self.evaporator.compute()	
		self.postProcess(self.evaporator)
	
class Cooling(ThermodynamicalProcess):
	label = "Cooling"
	description = F.ModelDescription("Cooling process at constant pressure", show = True)
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/Cooling.svg")
	condenser = F.SubModelGroup(TC.Condenser, 'FG', label = 'Condenser')
	inputs = F.SuperGroup(['fluidSource', condenser])

	############# Methods ###############
	def compute(self):
		self.initCompute(self.fluidSource.fluidName)
		# Connect components
		self.connectPorts(self.fluidSource.outlet, self.condenser.inlet)
		self.connectPorts(self.condenser.outlet, self.fluidSink.inlet)
		self.fluidSource.compute()
		self.condenser.compute()	
		self.postProcess(self.condenser)

class ThermodynamicalProcessTwoStreams(ThermodynamicalCycle):
	############# Inputs #############
	fluidSource1 = F.SubModelGroup(TC.FluidSource, 'FG', label = 'Inlet 1')
	fluidSource2 = F.SubModelGroup(TC.FluidSource, 'FG', label = 'Inlet 2')
	fluidSink1 = F.SubModelGroup(TC.FluidSink, 'FG', label = 'Outlet 1')
	fluidSink2 = F.SubModelGroup(TC.FluidSink, 'FG', label = 'Outlet 2')
	inputs = F.SuperGroup([fluidSource1, fluidSource2, fluidSink1, fluidSink2])
	
	# Model View
	inputView = F.ModelView(ioType = "input", superGroups = [inputs], autoFetch = True)
	
	############# Results #############
	QDot = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'heat flow rate in')
	NTU = F.Quantity(label = 'NTU')
	Cr = F.Quantity(label = 'capacity ratio')
	energyResults = F.FieldGroup([QDot, NTU, Cr], label = "Energy")
	energyBalanceResults = F.SuperGroup([energyResults], label = "Energy balance")
	
	# Model View
	resultView = F.ModelView(ioType = "output", superGroups = ['resultStates', energyBalanceResults])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	############# Methods ###############
	def postProcess(self, component):
		super(ThermodynamicalProcessTwoStreams, self).postProcess(300)
		self.QDot = component.QDot
		self.NTU = component.NTU
		self.Cr = component.Cr

class HeatExchangerTwoStreams(ThermodynamicalProcessTwoStreams):
	label = "Heat Exchanger (two streams)"
	description = F.ModelDescription("Parameteric model for heat exchange between two streams", show = True)
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/HeatExchanger.svg")	
	heatExchanger = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label  = 'Heat exchanger')
	inputs = F.SuperGroup(['fluidSource1', 'fluidSource2', heatExchanger])
	
	def __init__(self):
		self.fluidSource2.T2 = (350, 'K')
	
	def compute(self):
		self.cycleDiagram.enable = False
		self.initCompute(self.fluidSource1.fluidName)
		# Connect components
		self.connectPorts(self.fluidSource1.outlet, self.heatExchanger.inlet1)
		self.connectPorts(self.heatExchanger.outlet1, self.fluidSink1.inlet)
		self.connectPorts(self.fluidSource2.outlet, self.heatExchanger.inlet2, fluid = self.fluidSource2.fluidName)
		self.connectPorts(self.heatExchanger.outlet2, self.fluidSink2.inlet, fluid = self.fluidSource2.fluidName)
		self.fluidSource1.compute()
		self.fluidSource2.compute()
		self.heatExchanger.compute()
		self.heatExchanger.computeStream1()
		self.heatExchanger.computeStream2()	
		self.postProcess(self.heatExchanger)
