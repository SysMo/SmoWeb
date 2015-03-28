'''
Created on Mar 25, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
import numpy as np
import smo.model.fields as F
import ThermodynamicComponents as TC
from smo.media.MaterialData import Fluids
from smo.model.model import NumericalModel
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from smo.web.modules import RestModule
import smo.web.exceptions as E
import Ports as P

class CycleIterator(object):
	def __init__(self, cycle, hTolerance = 1.0, maxNumIter = 100):
		self.cycle = cycle
		self.hTolerance = hTolerance
		self.maxNumIter = maxNumIter
		
	def saveOldValues(self):
		for i in range(self.ncp):
			self.old_h[i] = self.cycle.fp[i].h	
			self.old_T[i] = self.cycle.fp[i].T

	def computeChange(self):
		for i in range(self.ncp):			
			self.change_h[i] = self.cycle.fp[i].h - self.old_h[i]
		change = np.sqrt(np.sum(self.change_h**2))
		print "Change: {}".format(change)
		return change
		
	def checkConvergence(self):
		self.converged = self.computeChange() < self.hTolerance
		return self.converged
		
	def run(self):
		self.converged = False
		self.ncp = len(self.cycle.fp)
		self.old_h = np.zeros((self.ncp))
		self.old_T = np.zeros((self.ncp))
		self.change_h = np.zeros((self.ncp))
		i = 0
		self.cycle.computeCycle()
		#self.printValues()
		while (i < self.maxNumIter):			
			self.saveOldValues()
			self.cycle.computeCycle()
			print i
			self.checkConvergence()
			if (self.converged):
				break
			i += 1
			
		if (not self.converged):
			raise E.ConvergenceError('Solution did not converge')
		
	def printValues(self):
		print [fp.T for fp in self.cycle.fp]
		print [fl.mDot for fl in self.cycle.flows]
			
class ThermodynamicalCycle(NumericalModel):
	abstract = True
	#================ Inputs ================#
	# Cycle diagram
	cycleDiagram = F.SubModelGroup(TC.CycleDiagram, 'inputs', label = 'Diagram settings')
	#================ Results ================#
	#---------------- Fields ----------------#
	cycleStatesTable = F.TableView((
		('T', F.Quantity('Temperature', default = (1, 'degC'))),
		('p', F.Quantity('Pressure', default = (1, 'bar'))),
		('rho', F.Quantity('Density', default = (1, 'kg/m**3'))),
		('h', F.Quantity('SpecificEnthalpy', default = (1, 'kJ/kg'))),
		('s', F.Quantity('SpecificEntropy', default = (1, 'kJ/kg-K'))),
		('q', F.Quantity()),
		('dT', F.Quantity('TemperatureDifference', default = (1, 'degC'))),
		('mDot', F.Quantity('MassFlowRate', default = (1, 'kg/min'))),
		('b', F.Quantity('SpecificEnergy', default = (1, 'kJ/kg')))
		), label="Cycle states")
						
	cycleStates = F.ViewGroup([cycleStatesTable], label = "States")
	resultStates = F.SuperGroup([cycleStates], label="States")
	#---------------- Cycle diagram -----------#
	phDiagram = F.Image(default='', width=880, height=550)
	cycleDiagramVG = F.ViewGroup([phDiagram], label = "P-H Diagram")
	resultDiagrams = F.SuperGroup([cycleDiagramVG], label = "Diagrams")
	# Info fields
	cycleTranscritical = F.Boolean(default = False)
	cycleSupercritical = F.Boolean(default = False)
	
	def initCompute(self, fluid):
		# Create fluid points
		self.fluid = Fluid(fluid)
		self.fp = [] #[FluidState(fluid) for _ in range(numPoints)]
		self.flows = []
		self.cycleIterator = CycleIterator(self)

	def connectPorts(self, port1, port2):
		fp = FluidState(self.fluid)
		flow = P.FluidFlow()
		self.fp.append(fp)
		self.flows.append(flow)
		port1.state = fp
		port2.state = fp
		port1.flow = flow
		port2.flow = flow
	
	
	def postProcess(self, TAmbient):
		## State diagram
		if (self.cycleDiagram.enable):
			self.createStateDiagram()
		## Table of states
		self.cycleStatesTable.resize(len(self.fp))
		for i in range(len(self.fp)):
			fp = self.fp[i]
			self.cycleStatesTable[i] = (fp.T, fp.p, fp.rho, fp.h, fp.s, fp.q, fp.dT, self.flows[i].mDot, fp.b(TAmbient))
		# Select the zero for the exergy scale
		fp = FluidState(self.fluid)
		fp.update_Tp(TAmbient, 1e5)
		b0 = fp.b(TAmbient)
		self.cycleStatesTable['b'] -= b0
		
	def createStateDiagram(self):
		ncp = len(self.fp)
		fluidLines = []
		for i in range(ncp):
			fluidLines.append((self.fp[i], self.fp[(i + 1) % ncp]))
		self.phDiagram = self.cycleDiagram.draw(self.fluid, self.fp, fluidLines)	

	def setPLow(self, p):
		if (self.fluid.tripple['p'] < p < self.fluid.critical['p']):
			self.pLow = p
			sat = self.fluid.saturation_p(p)
			self.TEvaporation = sat['TsatL']
		elif (p > self.fluid.critical['p']):
			self.pLow = p
			self.cycleSupercritical = True
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

	
class HeatPumpCycle(ThermodynamicalCycle):	
	abstract = True
	#================ Inputs ================#
	fluidName = F.Choices(Fluids, default = 'R134a', label = 'working fluid')
	mDot = F.Quantity('MassFlowRate', default = (1, 'kg/min'), label = ' fluid flow rate')
	pHighMethod = F.Choices(OrderedDict((
		('P', 'pressure'),
		('T', 'temperature'),
	)), label = 'high side defined by')
	TCondensation = F.Quantity('Temperature', default = (40, 'degC'), label = 'condensation temperature', show = "self.pHighMethod == 'T'")
	pHigh = F.Quantity('Pressure', default = (40, 'bar'), label = 'high pressure', show = "self.pHighMethod == 'P'")

	pLowMethod = F.Choices(OrderedDict((
		('P', 'pressure'),
		('T', 'temperature'),
	)), label = 'low side defined by')
	TEvaporation = F.Quantity('Temperature', default = (-10, 'degC'), label = 'evaporation temperature', show = "self.pLowMethod == 'T'")
	pLow = F.Quantity('Pressure', default = (1, 'bar'), label = 'low pressure', show = "self.pLowMethod == 'P'")
	TAmbient = F.Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature', description = 'used as reference temperature to calculate exergy')	
	workingFluidGroup = F.FieldGroup(['fluidName', 'mDot', 
		pHighMethod, TCondensation, pHigh, 
		pLowMethod, TEvaporation, pLow, TAmbient], 'Cycle parameters')
	#================ Results ================#
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

	def initCompute(self, fluid):
		ThermodynamicalCycle.initCompute(self, fluid)
		# Set high and low pressures
		if (self.pLowMethod == 'P'):
			self.setPLow(self.pLow)
		else:
			self.setTEvaporation(self.TEvaporation)
		
		if (self.pHighMethod == 'P'):
			self.setPHigh(self.pHigh)
		else:
			self.setTCondensation(self.TCondensation)
		if (self.pLow >= self.pHigh):
			raise ValueError('The low cycle pressure must be less than the high cycle pressure')


class HeatPumpCyclesDoc(RestModule):
	label = 'Documentation'

class HeatEngineCycle(ThermodynamicalCycle):
	abstract = True
	#================ Inputs ================#
	fluidName = F.Choices(Fluids, default = 'R134a', label = 'refrigerant')
	mDot = F.Quantity('MassFlowRate', default = (1, 'kg/min'), label = ' refrigerant flow rate')
	pHighMethod = F.Choices(OrderedDict((
		('P', 'pressure'),
		('T', 'temperature'),
	)), label = 'high side defined by')
	TEvaporation = F.Quantity('Temperature', default = (-10, 'degC'), label = 'evaporation temperature', show = "self.pHighMethod == 'T'")
	pHigh = F.Quantity('Pressure', default = (40, 'bar'), label = 'high pressure', show = "self.pHighMethod == 'P'")

	pLowMethod = F.Choices(OrderedDict((
		('P', 'pressure'),
		('T', 'temperature'),
	)), label = 'low side defined by')
	pLow = F.Quantity('Pressure', default = (1, 'bar'), label = 'low pressure', show = "self.pLowMethod == 'P'")
	TCondensation = F.Quantity('Temperature', default = (40, 'degC'), label = 'condensation temperature', show = "self.pLowMethod == 'T'")
	TAmbient = F.Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature', description = 'used as reference temperature to calculate exergy')	
	workingFluidGroup = F.FieldGroup(['fluidName', 'mDot', 
		pHighMethod, TEvaporation, pHigh, 
		pLowMethod, TCondensation, pLow, TAmbient], 'Cycle parameters')
	#================ Results ================#
	eta = F.Quantity('Efficiency', label = 'cycle efficiency')
	etaCarnot = F.Quantity('Efficiency', label = 'Carnot efficiency', description = 'efficiency of Carnot cycle between the high (boiler out) temperature and the low (condenser out) tempreature')
	etaSecondLaw = F.Quantity('Efficiency', label = 'second law efficiency', description = 'ratio or real cycle efficiency over Carnot efficiency')
	efficiencyFieldGroup = F.FieldGroup([eta, etaCarnot, etaSecondLaw], 'Efficiency')

	def setTCondensation(self, T):
		if (self.fluid.tripple['T'] < T < self.fluid.critical['T']):
			self.TCondensation = T
			sat = self.fluid.saturation_T(T)
			self.pLow = sat['psatL']
		else:
			raise ValueError('Condensation temperature ({} K) must be between {} K and {} K'.format(T, self.fluid.tripple['T'], self.fluid.critical['T']))

	def setTEvaporation(self, T):
		if (self.fluid.tripple['T'] < T < self.fluid.critical['T']):
			self.TEvaporation = T
			sat = self.fluid.saturation_T(T)
			self.pHigh = sat['psatL']
		else:
			raise ValueError('Evaporation temperature ({} K) must be between {} K and {} K'.format(T, self.fluid.tripple['T'], self.fluid.critical['T']))

	def initCompute(self, fluid):
		ThermodynamicalCycle.initCompute(self, fluid)
		# Set high and low pressures
		if (self.pLowMethod == 'P'):
			self.setPLow(self.pLow)
		else:
			self.setTCondensation(self.TCondensation)
		
		if (self.pHighMethod == 'P'):
			self.setPHigh(self.pHigh)
		else:
			self.setTEvaporation(self.TEvaporation)
		if (self.pLow >= self.pHigh):
			raise ValueError('The low cycle pressure must be less than the high cycle pressure')

class HeatEngineCyclesDoc(RestModule):
	label = 'Documentation'
	
class LiquefactionCycle(ThermodynamicalCycle):
	abstract = True
	#================ Inputs ================#
	fluidName = F.Choices(Fluids, default = 'R134a', label = 'liquefied fluid')
	mDot = F.Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'inlet flow rate')
	pIn = F.Quantity('Pressure', default = (1, 'bar'), label = 'inlet gas pressure')
	TIn = F.Quantity('Temperature', default = (15, 'degC'), label = 'inlet gas temperature')
	pHigh = F.Quantity('Pressure', default = (40, 'bar'), label = 'compressor high pressure')
	pLiquid = F.Quantity('Pressure', default = (2, 'bar'), label = 'liquid pressure')
	TAmbient = F.Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature', description = 'used as reference temperature to calculate exergy')	
	workingFluidGroup = F.FieldGroup(['fluidName', 'mDot', pIn, TIn, 
		pHigh, pLiquid, TAmbient], 'Cycle parameters')
	#================ Results ================#
	liqEnergy = F.Quantity('SpecificEnergy', default = (1, 'kJ/kg'), label = 'liquefaction energy')
	minLiqEnergy = F.Quantity('SpecificEnergy', default = (1, 'kJ/kg'), label = 'min. liquefaction energy', 
		description = 'minimum energy required for liquefaction in an ideal carnot cycle; \
			equal to the difference in exergies between initial and final state')
	etaSecondLaw = F.Quantity('Efficiency', label = 'figure of merit (FOM)', 
		description = 'minimum energy required for liquefaction to the actual energy required \
			in the cycle; equivalent to second law efficiency')
	efficiencyFieldGroup = F.FieldGroup([liqEnergy, minLiqEnergy, etaSecondLaw], 'Efficiency')
	
class LiquefactionCyclesDoc(RestModule):
	label = 'Documentation'
	