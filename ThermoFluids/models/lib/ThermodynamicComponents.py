'''
Created on Mar 21, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
from smo.model.model import NumericalModel
import smo.model.fields as F
from smo.media.CoolProp.CoolProp import Fluid, FluidState


class CycleComponent(NumericalModel):
	abstract = True
	w = F.Quantity('Power', default = (0, 'kW'), label = 'specific work')
	qIn = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'specific heat in')
	
class ThermodynamicalCycle(NumericalModel):
	abstract = True
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
	diagram = F.Image(default='', width=880, height=550)
	diagramViewGroup = F.ViewGroup([diagram], label = "P-H Diagram")
	resultDiagrams = F.SuperGroup([diagramViewGroup], label = "Diagrams")
	
	def initCompute(self, fluid, numPoints):
		self.fp = [FluidState(fluid) for i in range(numPoints)]
		self.fluid = Fluid(fluid)
		
	def postProcess(self, TAmbient):
		## State diagram
		self.createStateDiagram()
		## Table of states
		self.cycleStatesTable.resize(len(self.fp))
		for i in range(len(self.fp)):
			fp = self.fp[i]
			self.cycleStatesTable[i] = (fp.T, fp.p, fp.rho, fp.h, fp.s, fp.q, fp.b(TAmbient))

class Compressor(CycleComponent):
	modelType = F.Choices(OrderedDict((
		('S', 'isentropic'),
		('T', 'isothermal'),
	)), label = 'compressor model')
	eta = F.Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency', show = "self.modelType == 'S'")
	fQ = F.Quantity(default = 0, minValue = 0, maxValue = 1, label = 'heat loss factor', show="self.modelType == 'S'")
	FG = F.FieldGroup([modelType, eta, fQ], label = 'Compressor')
	modelBlocks = []

	def compute(self, pOut):
		self.outlet.update_ps(pOut, self.inlet.s)
		wIdeal = self.outlet.h - self.inlet.h
		self.w = wIdeal / self.eta
		self.qIn = - self.fQ * self.w
		delta_h = self.w + self.qIn
		self.outlet.update_ph(pOut, self.inlet.h + delta_h)

class Turbine(CycleComponent):
	eta = F.Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency')
	FG = F.FieldGroup([eta], label = 'Turbine')
	modelBlocks = []
	
	def compute(self, pOut):
		self.outlet.update_ps(pOut, self.inlet.s)
		wIdeal = self.outlet.h - self.inlet.h
		self.w = wIdeal * self.eta
		self.qIn = 0
		delta_h = self.w + self.qIn
		self.outlet.update_ph(pOut, self.inlet.h + delta_h)
	
class IsobaricHeatExchanger(CycleComponent):
	etaThermal = F.Quantity(default = 0.9, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.computeMethod == "eta"')
	TExt = F.Quantity('Temperature', default = (30, 'degC'), label = 'external temperature', show = 'self.computeMethod == "eta"')
	qOutlet = F.Quantity(default = 0, minValue = 0, maxValue = 1, label = 'outlet vapor quality', show = 'self.computeMethod == "Q"')
	TOutlet = F.Quantity('Temperature', default = (40, 'degC'), label = 'outlet temperature', show = 'self.computeMethod == "T"')
	hOutlet = F.Quantity('SpecificEnthalpy', default = (100, 'kJ/kg'), minValue = -1e10, label = 'outlet enthalpy', show = 'self.computeMethod == "H"')
	modelBlocks = []

	def compute(self):
		pIn = self.inlet.p
		if (self.computeMethod == 'eta'):
			self.outlet.update_Tp(self.TExt, pIn)
			hOut = (1 - self.etaThermal) * self.inlet.h + self.etaThermal * self.outlet.h
			self.outlet.update_ph(pIn, hOut)
		elif (self.computeMethod == 'dT'):
			self.outlet.update('P', pIn, 'dT', self.dTOutlet)
		elif (self.computeMethod == 'Q'):
			self.outlet.update_pq(pIn, self.qOutlet)
		elif (self.computeMethod == 'T'):
			self.outlet.update_Tp(self.TOutlet, pIn)
		elif (self.computeMethod == 'H'):
			self.outlet.update_ph(pIn, self.hOutlet)
		else:
			raise ValueError('Unknown compute method {}'.format(self.computeMethod))
		
		self.qIn = self.outlet.h - self.inlet.h
		
class Evaporator(IsobaricHeatExchanger):
	computeMethod = F.Choices(OrderedDict((
		('dT', 'super-heating'),
		('Q', 'vapor quality'),
		('eta', 'thermal efficiency'),
		('T', 'temperature'),
		('H', 'enthalpy'),
	)), label = 'compute outlet by')
	dTOutlet = F.Quantity('TemperatureDifference', default = (10, 'degC'), minValue = 1e-3, maxValue = 1e10, 
						label = 'outlet superheating', show = 'self.computeMethod == "dT"')
	FG = F.FieldGroup(['computeMethod', 'etaThermal', 'TExt', 'dTOutlet', 
			'TOutlet', 'qOutlet', 'hOutlet'], 
			label = 'Evaporator')
	modelBlocks = []

class Condenser(IsobaricHeatExchanger):
	computeMethod = F.Choices(OrderedDict((
		('dT', 'sub-cooling'),
		('Q', 'vapor quality'),
		('eta', 'thermal efficiency'),
		('T', 'temperature'),
		('H', 'enthalpy'),
	)), label = 'compute outlet by')
	dTOutlet = F.Quantity('TemperatureDifference', default = (-10, 'degC'), minValue = -1e10, maxValue = -1e-3, 
						label = 'outlet subcooling', show = 'self.computeMethod == "dT"')
	FG = F.FieldGroup(['computeMethod', 'etaThermal', 'TExt', 'dTOutlet', 
			'TOutlet', 'qOutlet', 'hOutlet'], 
			label = 'Condenser')
	modelBlocks = []

class HeatExchangerTwoStreams(CycleComponent):
	abstract = True
	eta = F.Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency')
	FG = F.FieldGroup([eta], label = 'Heat exchanger')
	def compute(self, m1Dot, m2Dot):
		self.outlet1.update_Tp(self.inlet2.T, self.inlet1.p)
		self.outlet2.update_Tp(self.inlet1.T, self.inlet2.p)
		dH1DotMax = m1Dot * (self.inlet1.h - self.outlet1.h)
		dH2DotMax = m2Dot * (self.inlet2.h - self.outlet2.h)
		if (abs(dH1DotMax) > abs(dH2DotMax)):
			self.QDot = dH2DotMax * self.eta
		else:
			self.QDot = -dH1DotMax * self.eta
		self.outlet1.update_ph(self.inlet1.p, self.inlet1.h + self.QDot / m1Dot)
		self.outlet2.update_ph(self.inlet2.p, self.inlet2.h - self.QDot / m2Dot)
	def __str__(self):
		return """
Inlet 1: T = {self.inlet1.T}, p = {self.inlet1.p}, q = {self.inlet1.q}, h = {self.inlet1.h} 
Outlet 1: T = {self.outlet1.T}, p = {self.outlet1.p}, q = {self.outlet1.q}, h = {self.outlet1.h} 
Inlet 2: T = {self.inlet2.T}, p = {self.inlet2.p}, q = {self.inlet2.q}, h = {self.inlet2.h}
Outlet2: T = {self.outlet2.T}, p = {self.outlet2.p}, q = {self.outlet2.q}, h = {self.outlet2.h}
		""".format(self = self)
	@staticmethod
	def test():
		fp = [FluidState('Water') for _ in range(4)]
		he = HeatExchangerTwoStreams()
		he.inlet1 = fp[0]
		he.outlet1 = fp[1]
		he.inlet2 = fp[2]
		he.outlet2 = fp[3]

		he.inlet1.update_Tp(80 + 273.15, 1e5)
		he.inlet2.update_Tp(20 + 273.15, 1e5)
		m1Dot = 1.
		m2Dot = 1.
		
		he.compute(m1Dot, m2Dot)
		print he

if __name__ == '__main__':
	HeatExchangerTwoStreams.test()