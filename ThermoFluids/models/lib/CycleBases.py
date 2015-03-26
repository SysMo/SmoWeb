'''
Created on Mar 25, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
import smo.model.fields as F
import ThermodynamicComponents as TC
from smo.media.MaterialData import Fluids
from smo.model.model import NumericalModel
from smo.media.CoolProp.CoolProp import Fluid, FluidState

class ThermodynamicalCycle(NumericalModel):
	abstract = True
	#================ Inputs ================#
	cycleDiagram = F.SubModelGroup(TC.CycleDiagram, 'inputs', label = 'Diagram settings')
	#================ Results ================#
	#---------------- Fields ----------------#
	cycleStatesTable = F.TableView((
		('T', F.Quantity('Temperature', default = (1, 'K'))),
		('p', F.Quantity('Pressure', default = (1, 'bar'))),
		('rho', F.Quantity('Density', default = (1, 'kg/m**3'))),
		('h', F.Quantity('SpecificEnthalpy', default = (1, 'kJ/kg'))),
		('s', F.Quantity('SpecificEntropy', default = (1, 'kJ/kg-K'))),
		('q', F.Quantity()),
		('b', F.Quantity('SpecificEnergy', default = (1, 'kJ/kg')))
		), label="Cycle states")
						
	cycleStates = F.ViewGroup([cycleStatesTable], label = "States")
	resultStates = F.SuperGroup([cycleStates], label="States")
	#---------------- Cycle diagram -----------#
	phDiagram = F.Image(default='', width=880, height=550)
	cycleDiagramVG = F.ViewGroup([phDiagram], label = "P-H Diagram")
	resultDiagrams = F.SuperGroup([cycleDiagramVG], label = "Diagrams")
	
	def initCompute(self, fluid, numPoints):
		self.fp = [FluidState(fluid) for i in range(numPoints)]
		self.fluid = Fluid(fluid)

	def createStateDiagram(self):
		ncp = len(self.fp)
		fluidLines = []
		for i in range(ncp):
			fluidLines.append((self.fp[i], self.fp[(i + 1) % ncp]))
		self.phDiagram = self.cycleDiagram.draw(self.fluid, self.fp, fluidLines)	
	
	def postProcess(self, TAmbient):
		## State diagram
		self.createStateDiagram()
		## Table of states
		self.cycleStatesTable.resize(len(self.fp))
		for i in range(len(self.fp)):
			fp = self.fp[i]
			self.cycleStatesTable[i] = (fp.T, fp.p, fp.rho, fp.h, fp.s, fp.q, fp.b(TAmbient))


class HeatPumpCycle(ThermodynamicalCycle):	
	abstract = True
	#================ Inputs ================#
	# Cycle settings
	fluidName = F.Choices(Fluids, default = 'R134a', label = 'fluid')
	TAmbient = F.Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature', description = 'used as reference temperature to calculate exergy')	
	mDotRefrigerant = F.Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'refrigerant flow rate')
	pHighMethod = F.Choices(OrderedDict((
		('T', 'temperature'),
		('P', 'pressure'),
	)), label = 'high side defined by')
	TCondensation = F.Quantity('Temperature', default = (40, 'degC'), label = 'condensation temperature', show = "self.pHighMethod == 'T'")
	pHigh = F.Quantity('Pressure', default = (40, 'bar'), label = 'high pressure', show = "self.pHighMethod == 'P'")

	pLowMethod = F.Choices(OrderedDict((
		('T', 'temperature'),
		('P', 'pressure'),
	)), label = 'low side defined by')
	TEvaporation = F.Quantity('Temperature', default = (-10, 'degC'), label = 'evaporation temperature', show = "self.pLowMethod == 'T'")
	pLow = F.Quantity('Pressure', default = (1, 'bar'), label = 'low pressure', show = "self.pLowMethod == 'P'")
	workingFluidGroup = F.FieldGroup([fluidName, TAmbient, mDotRefrigerant, 
		pHighMethod, TCondensation, pHigh, 
		pLowMethod, TEvaporation, pLow], 'Refrigerant')
	#================ Results ================#
	cycleTranscritical = F.Boolean(default = False)
	COPCooling = F.Quantity(label = 'COP (cooling)')
	COPHeating = F.Quantity(label = 'COP (heating)')
	efficiencyFieldGroup = F.FieldGroup([COPCooling, COPHeating], 'Efficiency')

	def setTCondensation(self, T):
		if (self.fluid.tripple['T'] < T < self.fluid.critical['T']):
			self.TCondensation = T
			sat = self.fluid.saturation_T(T)
			self.pHigh = sat['psatL']
		else:
			raise ValueError('Condensation temperature ({} K) must be between {} K and {} K'.format(T, self.fluid.tripple['T'], self.fluid.critical['T']))

	def setTEvaporation(self, T):
		if (self.fluid.tripple['T'] < T < self.fluid.critical['T']):
			self.TEvaporation = T
			sat = self.fluid.saturation_T(T)
			self.pLow = sat['psatL']
		else:
			raise ValueError('Evaporation temperature ({} K) must be between {} K and {} K'.format(T, self.fluid.tripple['T'], self.fluid.critical['T']))

	def setPLow(self, p):
		if (self.fluid.tripple['p'] < p < self.fluid.critical['p']):
			self.pLow = p
			sat = self.fluid.saturation_p(p)
			self.TEvaporation = sat['TsatL']
		else:
			raise ValueError('PLow  ({} bar) must be between {} bar and {} bar'.format(p/1e5, self.fluid.tripple['p']/1e5, self.fluid.critical['p']/1e5))

	def setPHigh(self, p):
		if (self.fluid.tripple['p'] < p < self.fluid.critical['p']):
			self.pHigh = p
			sat = self.fluid.saturation_p(p)
			self.TCondensation = sat['TsatL']
		elif (p > self.fluid.critical['p']):
			self.pHigh = p
			self.cycleTranscritical = True
		else:
			raise ValueError('PHigh  ({} bar) must be between {} bar and {} bar'.format(p/1e5, self.fluid.tripple['p']/1e5, self.fluid.critical['p']/1e5))

	def initCompute(self, **kwargs):
		super(HeatPumpCycle, self).initCompute(**kwargs)
		if (self.pLowMethod == 'P'):
			self.setPLow(self.pLow)
		else:
			self.setTEvaporation(self.TEvaporation)
		
		if (self.pHighMethod == 'P'):
			self.setPHigh(self.pHigh)
		else:
			self.setTCondensation(self.TCondensation)


class HeatEngineCycle(ThermodynamicalCycle):
	abstract = True