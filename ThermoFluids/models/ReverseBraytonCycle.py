'''
Created on Nov 09, 2014
@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import os
from collections import OrderedDict
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
from smo.web.modules import RestModule
from smo.media.MaterialData import Fluids
from smo.media.diagrams.StateDiagrams import PHDiagram
import lib.ThermodynamicComponents as TC
import smo.web.exceptions as E 

class HeatPumpCycle(TC.ThermodynamicalCycle):	
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
# 	COPCarnotCooling = F.Quantity(label = 'COP Carnot (cooling)', description = 'COP(cooling) of Carnot cycle between the high (condenser) temperature and the low (evaporator) tempreature')
# 	COPCarnotHeating = F.Quantity(label = 'COP Carnot (heating)', description = 'COP(heating) of Carnot cycle between the high (condenser) temperature and the low (evaporator) tempreature')
# 	etaSecondLawCooling = F.Quantity('Efficiency', label = 'efficiency (cooling)', description = 'second law efficiency: ratio or real cycle COP over Carnot COP')
# 	etaSecondLawHeating = F.Quantity('Efficiency', label = 'efficiency (heating)', description = 'second law efficiency: ratio or real cycle COP over Carnot COP')
#	efficiencyFieldGroup = F.FieldGroup([COPCooling, COPHeating, COPCarnotCooling, COPCarnotHeating, etaSecondLawCooling, etaSecondLawHeating], 'Efficiency')
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
		


class ReverseBraytonCycle(HeatPumpCycle):
	label = "Reverse Brayton cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/ReverseBraytonCycle.svg")
	description = F.ModelDescription("Basic Brayton cycle used in refrigerators and air conditioners", show = True)

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
	exampleAction = ServerAction("loadEg", label = "Examples", options = (('CO2TranscriticalCycle', 'CO2 transcritial cycle'),) )
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
	def compute(self):
		self.initCompute(fluid = self.fluidName, numPoints = 4)
		self.evaporator.outlet = self.compressor.inlet = self.fp[0]
		self.compressor.outlet = self.condenser.inlet = self.fp[1]
		self.condenser.outlet = self.throttleValve.inlet = self.fp[2]
		self.throttleValve.outlet = self.evaporator.inlet = self.fp[3]
		
		# Cycle iterations
		absToleranceEnthalpy = 1.0;
		maxNumIter = 20
		i = 0
		self.fp[0].update_pq(self.pLow, 0)
		while (i < maxNumIter):
			hOld = self.fp[0].h
			self.computeCycle()
			hNew = self.fp[0].h
			if (abs(hOld - hNew) < absToleranceEnthalpy):
				break
		if (hOld - hNew >= absToleranceEnthalpy):
			raise E.ConvergenceError('Solution did not converge')

		# Results
		self.postProcess()
	
	def computeCycle(self):
		self.compressor.compute(self.pHigh)
		self.condenser.compute()
		self.throttleValve.compute(self.pLow)
		self.evaporator.compute()
		
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')
		
	def postProcess(self):
		super(ReverseBraytonCycle, self).postProcess(self.TAmbient)
		self.compressorPower = self.mDotRefrigerant * self.compressor.w
		self.compressorHeat = -self.mDotRefrigerant * self.compressor.qIn
		self.condenserHeat = -self.mDotRefrigerant * self.condenser.qIn
		self.evaporatorHeat = self.mDotRefrigerant * self.evaporator.qIn
		
		self.COPCooling = self.evaporatorHeat / self.compressorPower
		self.COPHeating = self.condenserHeat / self.compressorPower
# 		self.COPCarnotCooling = self.TEvaporation / (self.TCondensation - self.TEvaporation)
# 		self.COPCarnotHeating = self.TCondensation / (self.TCondensation - self.TEvaporation)
# 		self.etaSecondLawCooling = self.COPCooling / self.COPCarnotCooling
# 		self.etaSecondLawHeating = self.COPHeating / self.COPCarnotHeating

	def createStateDiagram(self):
		ncp = len(self.fp)
		fluidLines = []
		for i in range(ncp):
			fluidLines.append((self.fp[i], self.fp[(i + 1) % ncp]))
		self.phDiagram = self.cycleDiagram.draw(self.fluid, self.fp, fluidLines)	

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
		
class HeatPumpDoc(RestModule):
	name = 'HeatPumpDoc'
	label = 'Heat Pump (Docs)'
	template = 'documentation/html/HeatPumpDoc.html'
		
if __name__ == '__main__':
	#IsentropicCompression.test()
	pass