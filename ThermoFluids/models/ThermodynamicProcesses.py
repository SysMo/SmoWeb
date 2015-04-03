from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from collections import OrderedDict
from lib.CycleBases import ThermodynamicalCycle

class ThermodynamicalProcess(ThermodynamicalCycle):
	############# Inputs #############
	fluidSource = F.SubModelGroup(TC.FluidSource, 'FG', label = 'Initial State')
	fluidSink = F.SubModelGroup(TC.FluidSink, 'FG', label = 'Final State')
	inputs = F.SuperGroup([fluidSource, fluidSink])
	
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model View
	inputView = F.ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
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
	turbine = F.SubModelGroup(TC.Turbine, 'FG', label = 'Turbine', show="self.processType == 'S'")
	throttleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', show="false")
	processType = F.Choices(options = OrderedDict((
														('S', 'isentropic'),
														('H', 'isenthalpic'),
													)), default = 'S', label = "process type")
	processTypeFG = F.FieldGroup([processType], label = "Process type")
	inputs = F.SuperGroup(['fluidSource', 'fluidSink', processTypeFG, turbine, throttleValve])
	
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
