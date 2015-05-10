'''
Created on Mar 21, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import os
import math as m
from collections import OrderedDict
from smo.model.model import NumericalModel
import smo.model.fields as F
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from smo.media.diagrams.StateDiagrams import PHDiagram
from smo.web.modules import RestModule
import Ports as P

class CycleDiagram(NumericalModel):
	#================ Inputs ================#
	enable = F.Boolean(label = 'create process diagram', default = True)
	isotherms = F.Boolean(label = 'isotherms')
	temperatureUnit = F.Choices(OrderedDict((('K', 'K'), ('degC', 'degC'))), default = 'K', label="temperature unit", show="self.isotherms == true")
	isochores = F.Boolean(label = 'isochores')
	isentrops = F.Boolean(label = 'isentrops')
	qIsolines = F.Boolean(label = 'vapor quality isolines')
	diagramInputs = F.FieldGroup([enable, isotherms, temperatureUnit, isochores, isentrops, qIsolines], 
								label = 'Diagram')
	
	defaultMaxP = F.Boolean(label = 'default max pressure')
	defaultMaxT = F.Boolean(label = 'default max temperature')
	maxPressure = F.Quantity('Pressure', default = (1, 'bar'), label = 'max pressure', show="self.defaultMaxP == false")
	maxTemperature = F.Quantity('Temperature', default = (300, 'K'), label = 'max temperature', show="self.defaultMaxT == false")
	boundaryInputs = F.FieldGroup([defaultMaxP, defaultMaxT, maxPressure, maxTemperature],
								label = 'Value Limits')
	
	inputs = F.SuperGroup([diagramInputs, boundaryInputs], label = 'Diagram settings')
	modelBlocks = []
	
	def draw(self, fluid, fluidPoints, cycleLines):
		# Create diagram object
		diagram = PHDiagram(fluid.name, temperatureUnit = self.temperatureUnit)
		# Set limits
		pMax, TMax = None, None
		if not self.defaultMaxP:
			pMax = self.maxPressure
		if not self.defaultMaxT:
			TMax = self.maxTemperature
		diagram.setLimits(pMax = pMax, TMax = TMax)
		fig  = diagram.draw(isotherms=self.isotherms,
							isochores=self.isochores, 
							isentrops=self.isentrops, 
							qIsolines=self.qIsolines)
		ax = fig.get_axes()[0]		
		# Draw points
		i = 1
		for fp in fluidPoints:
			ax.semilogy(fp.h/1e3, fp.p/1e5, 'ko')
			ax.annotate('{}'.format(i), 
				xy = (fp.h/1e3, fp.p/1e5),
				xytext = (3, 2), textcoords = 'offset points',
				size = 'x-large')
			i += 1
		# Draw lines
		for (fp1, fp2) in cycleLines:
			ax.semilogy(
				[fp1.h/1e3, fp2.h/1e3], 
				[fp1.p/1e5, fp2.p/1e5],
				'k', linewidth = 2)
		# Export diagram to file
		fHandle, resourcePath  = diagram.export(fig)
		os.close(fHandle)
		return resourcePath

class CycleComponent(NumericalModel):
	abstract = True

class FluidSource_TP(CycleComponent):
	T = F.Quantity('Temperature', label = 'temperature')
	p = F.Quantity('Pressure', label = 'pressure')
	mDot = F.Quantity('MassFlowRate', label = 'mass flow rate')
	FG = F.FieldGroup([T, p, mDot], label = 'Compressor')
	modelBlocks = []
	#================== Ports =================#
	outlet = F.Port(P.ThermodynamicPort)
	#================== Methods =================#		
	def compute(self):
		self.outlet.flow.mDot = self.mDot
		self.outlet.state.update_Tp(self.T, self.p)
		
from smo.media.MaterialData import Fluids
StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)'),
))		
class FluidSource(CycleComponent):
	fluidName = F.Choices(options = Fluids, default = 'Water', label = 'fluid')	
	stateVariable1 = F.Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
	p1 = F.Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable1 == 'P'")
	T1 = F.Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
	rho1 = F.Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
	h1 = F.Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
	s1 = F.Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable1 == 'S'")
	q1 = F.Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable1 == 'Q'")
	stateVariable2 = F.Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
	p2 = F.Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
	T2 = F.Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
	rho2 = F.Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
	h2 = F.Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
	s2 = F.Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable2 == 'S'")
	q2 = F.Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable2 == 'Q'")
	mDot = F.Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mass flow')
	
	FG = F.FieldGroup([fluidName, stateVariable1, p1, T1, rho1, h1, s1, q1, 
						stateVariable2, p2, T2, rho2, h2, s2, q2, mDot], label = 'Compressor')
	modelBlocks = []
	#================== Ports ===================#
	outlet = F.Port(P.ThermodynamicPort)
	#================== Methods =================#
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]		
	
	def compute(self):
		self.outlet.flow.mDot = self.mDot
		self.outlet.state.update(
				self.stateVariable1, self.getStateValue(self.stateVariable1, suffix = "1"), 
				self.stateVariable2, self.getStateValue(self.stateVariable2, suffix = "2")
		)
		
class FluidSink(CycleComponent):
	modelBlocks = []
	p = F.Quantity('Pressure', default = (10, 'bar'), label = 'pressure')
	FG = F.FieldGroup([p])
	#================== Ports =================#
	inlet = F.Port(P.ThermodynamicPort)
	
class CycleComponent2FlowPorts(CycleComponent):
	abstract = True
	w = F.Quantity('SpecificEnergy', default = (0, 'kJ/kg'), label = 'specific work')
	qIn = F.Quantity('SpecificEnergy', default = (0, 'kJ/kg'), label = 'specific heat in')
	delta_h = F.Quantity('SpecificEnthalpy', label = 'enthalpy change (fluid)')
	WDot = F.Quantity('Power', default = (0, 'kW'), label = 'power')
	QDotIn = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'heat flow rate in')
	deltaHDot = F.Quantity('Power', label = 'enthalpy change (fluid)') 
	#================== Ports =================#
	inlet = F.Port(P.ThermodynamicPort)
	outlet = F.Port(P.ThermodynamicPort)
	#================== Methods =================#	
	def compute(self):
		self.outlet.flow.mDot = self.inlet.flow.mDot
	
	def postProcess(self):
		self.WDot = self.w * self.inlet.flow.mDot
		self.QDotIn = self.qIn * self.inlet.flow.mDot
		self.deltaHDot = self.delta_h * self.inlet.flow.mDot
	
class Compressor(CycleComponent2FlowPorts):
	modelType = F.Choices(OrderedDict((
		('S', 'isentropic'),
		('T', 'isothermal'),
	)), label = 'compressor model')
	etaS = F.Quantity('Efficiency', label = 'isentropic efficiency', show = "self.modelType == 'S'")
	fQ = F.Quantity('Fraction', default = 0., label = 'heat loss factor', show="self.modelType == 'S'")
	etaT = F.Quantity('Efficiency', label = 'isosthermal efficiency', show = "self.modelType == 'T'")
	dT = F.Quantity('TemperatureDifference', default = 0, label = 'temperature increase', show = "self.modelType == 'T'")
	FG = F.FieldGroup([modelType, etaS, fQ, etaT, dT], label = 'Compressor')
	modelBlocks = []
	#================== Methods =================#
	def compute(self, pOut):
		CycleComponent2FlowPorts.compute(self)
		if (pOut < self.inlet.state.p):
			raise ValueError('Outlet pressure must be higher than inlet pressure')
		if (self.modelType == 'S'):
			self.outlet.state.update_ps(pOut, self.inlet.state.s)
			wIdeal = self.outlet.state.h - self.inlet.state.h
			self.w = wIdeal / self.etaS
			self.qIn = - self.fQ * self.w
			self.delta_h = self.w + self.qIn
			self.outlet.state.update_ph(pOut, self.inlet.state.h + self.delta_h)
		else:
			self.outlet.state.update_Tp(self.inlet.state.T + self.dT, pOut)
			self.qIn = (self.outlet.state.s - self.inlet.state.s) * self.inlet.state.T
			wIdeal = self.outlet.state.h - self.inlet.state.h - self.qIn
			self.w = wIdeal / self.etaT
			self.qIn -= (self.w - wIdeal)

class Turbine(CycleComponent2FlowPorts):
	eta = F.Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency')
	FG = F.FieldGroup([eta], label = 'Turbine')
	modelBlocks = []
	#================== Methods =================#	
	def compute(self, pOut):
		if (pOut > self.inlet.state.p):
			raise ValueError('Outlet pressure must be lower than inlet pressure')
		CycleComponent2FlowPorts.compute(self)
		self.outlet.state.update_ps(pOut, self.inlet.state.s)
		wIdeal = self.outlet.state.h - self.inlet.state.h
		self.w = wIdeal * self.eta
		self.qIn = 0
		self.delta_h = self.w + self.qIn
		self.outlet.state.update_ph(pOut, self.inlet.state.h + self.delta_h)
	
class ThrottleValve(CycleComponent2FlowPorts):
	FG = F.FieldGroup([])
	modelBlocks = []
	#================== Methods =================#
	def compute(self, pOut):
		if (pOut > self.inlet.state.p):
			raise ValueError('Outlet pressure must be lower than inlet pressure')
		CycleComponent2FlowPorts.compute(self)
		self.outlet.state.update_ph(pOut, self.inlet.state.h)
		self.w = 0
		self.qIn = 0
		self.delta_h = 0

class IsobaricHeatExchanger(CycleComponent2FlowPorts):
	etaThermal = F.Quantity(default = 1.0, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.computeMethod == "eta"')
	TExt = F.Quantity('Temperature', default = (30, 'degC'), label = 'external temperature', show = 'self.computeMethod == "eta"')
	qOutlet = F.Quantity(default = 0, minValue = 0, maxValue = 1, label = 'outlet vapor quality', show = 'self.computeMethod == "Q"')
	TOutlet = F.Quantity('Temperature', default = (40, 'degC'), label = 'outlet temperature', show = 'self.computeMethod == "T"')
	hOutlet = F.Quantity('SpecificEnthalpy', default = (100, 'kJ/kg'), minValue = -1e10, label = 'outlet enthalpy', show = 'self.computeMethod == "H"')
	modelBlocks = []
	#================== Methods =================#
	def compute(self):
		CycleComponent2FlowPorts.compute(self)
		pIn = self.inlet.state.p
		if (self.computeMethod == 'eta'):
			self.outlet.state.update_Tp(self.TExt, pIn)
			hOut = (1 - self.etaThermal) * self.inlet.state.h + self.etaThermal * self.outlet.state.h
			self.outlet.state.update_ph(pIn, hOut)
		elif (self.computeMethod == 'dT'):
			self.outlet.state.update('P', pIn, 'dT', self.dTOutlet)
		elif (self.computeMethod == 'Q'):
			self.outlet.state.update_pq(pIn, self.qOutlet)
		elif (self.computeMethod == 'T'):
			self.outlet.state.update_Tp(self.TOutlet, pIn)
		elif (self.computeMethod == 'H'):
			self.outlet.state.update_ph(pIn, self.hOutlet)
		else:
			raise ValueError('Unknown compute method {}'.format(self.computeMethod))
		
		self.qIn = self.outlet.state.h - self.inlet.state.h
		self.delta_h = self.qIn
		self.w = 0
		
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
	#================== Inputs =================#
	computeMethod = F.Choices(OrderedDict((
		('EG',  'effectiveness (given)'),
		('EN', 'effectiveness (NTU)'),
	)), label = 'compute method')
	type = F.Choices(options = OrderedDict((
												('CF', 'counter flow'),
												('PF', 'parallel flow'),
												('EC', 'evaporation/condensation'),
											)), default = 'CF', label = "flow configuration",
						show = 'self.computeMethod == "EN"')
	epsGiven = F.Quantity('Efficiency', default = 1, label = 'effectiveness', show = 'self.computeMethod == "EG"')
	UA = F.Quantity('ThermalConductance', default = (1, 'kW/K'), label = 'UA', show = 'self.computeMethod == "EN"')
	QDot = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'heat flow rate in')
	FG = F.FieldGroup([computeMethod, epsGiven, UA, type], label = 'Heat exchanger')
	#================== Results =================#
	NTU = F.Quantity(label = 'NTU')
	Cr = F.Quantity(label = 'capacity ratio')
	epsilon = F.Quantity('ThermalConductance', label = 'effectiveness')
	modelBlocks = []
	#================== Ports =================#
	inlet1 = F.Port(P.ThermodynamicPort)
	outlet1 = F.Port(P.ThermodynamicPort)
	inlet2 = F.Port(P.ThermodynamicPort)
	outlet2 = F.Port(P.ThermodynamicPort)
	#================== Methods =================#
	def compute(self):
		self.outlet1.state.update_Tp(self.inlet2.state.T, self.inlet1.state.p)
		self.outlet2.state.update_Tp(self.inlet1.state.T, self.inlet2.state.p)
		dH1DotMax = self.inlet1.flow.mDot * (self.inlet1.state.h - self.outlet1.state.h)
		dH2DotMax = self.inlet2.flow.mDot * (self.inlet2.state.h - self.outlet2.state.h)
		if (abs(dH1DotMax) > abs(dH2DotMax)):
			if (self.computeMethod == 'EG'):
				self.epsilon = self.epsGiven
			else:
				self.computeNTU(dH2DotMax, dH1DotMax)
			self.QDot = dH2DotMax * self.epsilon
		else:
			if (self.computeMethod == 'EG'):
				self.epsilon = self.epsGiven
			else:
				self.computeNTU(dH1DotMax, dH2DotMax)
			self.QDot = -dH1DotMax * self.epsilon

	def computeStream1(self):
		m1Dot = self.outlet1.flow.mDot = self.inlet1.flow.mDot
		self.outlet1.state.update_ph(self.inlet1.state.p, self.inlet1.state.h + self.QDot / m1Dot)
	def computeStream2(self):
		m2Dot = self.outlet2.flow.mDot = self.inlet2.flow.mDot
		self.outlet2.state.update_ph(self.inlet2.state.p, self.inlet2.state.h - self.QDot / m2Dot)
	def computeNTU(self, dHDotMin, dHDotMax):
		deltaTInlet = self.inlet1.state.T - self.outlet1.state.T
		CMin = dHDotMin / deltaTInlet
		CMax = dHDotMax / deltaTInlet
		self.NTU = self.UA / abs(CMin)
		self.Cr = abs(CMin / CMax)
		if self.type == 'CF':
			self.NTU_counterFlow()
		elif self.type == 'PF':
			self.NTU_parallelFlow()
		elif self.type == 'EC':
			self.NTU_evaporation_condensation()
	def NTU_counterFlow(self):
		self.epsilon = (1 - m.exp(- self.NTU * (1 - self.Cr))) / (1 - self.Cr * m.exp(- self.NTU * (1 - self.Cr))) 
	def NTU_parallelFlow(self):
		self.epsilon = (1 - m.exp(- self.NTU * (1 + self.Cr))) / (1 + self.Cr)
	def NTU_evaporation_condensation(self):
		self.epsilon = 1 - m.exp(- self.NTU)
	def __str__(self):
		return """
Inlet 1: T = {self.inlet1.state.T}, p = {self.inlet1.state.p}, q = {self.inlet1.state.q}, h = {self.inlet1.state.h} 
Outlet 1: T = {self.outlet1.state.T}, p = {self.outlet1.state.p}, q = {self.outlet1.state.q}, h = {self.outlet1.state.h} 
Inlet 2: T = {self.inlet2.state.T}, p = {self.inlet2.state.p}, q = {self.inlet2.state.q}, h = {self.inlet2.state.h}
Outlet2: T = {self.outlet2.state.T}, p = {self.outlet2.state.p}, q = {self.outlet2.state.q}, h = {self.outlet2.state.h}
		""".format(self = self)
	@staticmethod
	def test():
		fp = [FluidState('Water') for _ in range(4)]
		he = HeatExchangerTwoStreams()
		he.inlet1.state = fp[0]
		he.outlet1.state = fp[1]
		he.inlet2.state = fp[2]
		he.outlet2.state = fp[3]

		he.inlet1.state.update_Tp(80 + 273.15, 1e5)
		he.inlet2.state.update_Tp(20 + 273.15, 1e5)
		m1Dot = 1.
		m2Dot = 1.
		
		he.compute(m1Dot, m2Dot)
		print he

class FlowJunction(CycleComponent):
	FG = F.FieldGroup([])
	modelBlocks = []
	#================== Ports =================#
	inletMain = F.Port(P.ThermodynamicPort)
	inlet2 = F.Port(P.ThermodynamicPort)
	outlet = F.Port(P.ThermodynamicPort)
	#================== Methods =================#
	def compute(self):
		HDotIn = self.inletMain.flow.mDot * self.inletMain.state.h \
			+ self.inlet2.flow.mDot * self.inlet2.state.h
		mDotIn = self.inletMain.flow.mDot + self.inlet2.flow.mDot
		hOut = HDotIn / mDotIn
		self.outlet.state.update_ph(self.inletMain.state.p, hOut)
		self.outlet.flow.mDot = mDotIn
		
class FlowSplitter(CycleComponent):
	frac1 = F.Quantity('Fraction', label = 'fraction to outlet 1')
	frac2 = F.Quantity('Fraction', label = 'fraction to outlet 2')
	FG = F.FieldGroup([frac1, frac2])
	modelBlocks = []
	#================== Ports =================#
	inlet = F.Port(P.ThermodynamicPort)
	outlet1 = F.Port(P.ThermodynamicPort)
	outlet2 = F.Port(P.ThermodynamicPort)
	#================== Methods =================#
	def compute(self):
		self.outlet1.flow.mDot = self.inlet.flow.mDot * self.frac1 / (self.frac1 + self.frac2)
		self.outlet2.flow.mDot = self.inlet.flow.mDot * self.frac2 / (self.frac1 + self.frac2)
		self.outlet1.state.update_Trho(self.inlet.state.T, self.inlet.state.rho)
		self.outlet2.state.update_Trho(self.inlet.state.T, self.inlet.state.rho)

class PhaseSeparator(CycleComponent):
	FG = F.FieldGroup([])
	modelBlocks = []
	#================== Ports =================#
	inlet = F.Port(P.ThermodynamicPort)
	outletLiquid = F.Port(P.ThermodynamicPort)
	outletVapor = F.Port(P.ThermodynamicPort)
	#================== Methods =================#
	def compute(self):
		if (0 < self.inlet.state.q < 1):
			fq = self.inlet.state.q
		else:
			fq = 1.0
		
		self.outletLiquid.state.update_pq(self.inlet.state.p, 0)
		self.outletLiquid.flow.mDot = (1 - fq) * self.inlet.flow.mDot
		#self.outletLiquid.flow.HDot = self.outletLiquid.flow.mDot * self.outletLiquid.state.h

		self.outletVapor.state.update_pq(self.inlet.state.p, 1)
		self.outletVapor.flow.mDot = fq * self.inlet.flow.mDot
		#self.outletVapor.flow.HDot = self.outletVapor.flow.mDot * self.outletVapor.state.h

class ThermodynamicComponentsDoc(RestModule):
	label = 'Thermodynamic components'

if __name__ == '__main__':
	HeatExchangerTwoStreams.test()
