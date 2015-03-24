'''
Created on Mar 20, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import os
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
from smo.media.MaterialData import Fluids
from smo.media.diagrams.StateDiagrams import PHDiagram
import lib.ThermodynamicComponents as TC
import smo.web.exceptions as E 

class RankineCycle(TC.ThermodynamicalCycle):
	label = "Rankine cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/RankineCycle.png",  height = 300)
	description = F.ModelDescription("Basic Rankine cycle used in power generation", show = True)
	
	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	fluidName = F.Choices(Fluids, default = 'Water', label = 'fluid')
	ambientTemperature = F.Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature')
	mDot = F.Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'mass flow rate', description = 'Mass flow rate of the working fluid through the pump')
	pLow = F.Quantity('Pressure', default = (1, 'bar'), label = 'low pressure')
	pHigh = F.Quantity('Pressure', default = (50, 'bar'), label = 'high pressure')
	workingFluidGroup = F.FieldGroup([fluidName, mDot, pLow, pHigh], 'Working fluid')	
	pump = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Pump')
	boiler = F.SubModelGroup(TC.Evaporator, 'FG', label = 'Boiler')
	turbine = F.SubModelGroup(TC.Turbine, 'FG', label = 'Turbine')
	condenser = F.SubModelGroup(TC.Condenser, 'FG', label = 'Condenser')
	inputs = F.SuperGroup([workingFluidGroup, pump, boiler, turbine, condenser])	
	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)

	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	#================ Results ================#
	#---------------- Energy flows -----------#
	pumpPower = F.Quantity('Power', default = (1, 'kW'), label = 'pump power')
	boilerHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'boiler heat in')
	turbinePower = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'turbine power')
	condenserHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'condenser heat out')
	flowFieldGroup = F.FieldGroup([pumpPower, boilerHeat, turbinePower, condenserHeat], label = 'Energy flows')
	eta = F.Quantity(label = 'cycle efficiency')
	etaCarnot = F.Quantity(label = 'Carnot efficiency', description = 'efficiency of Carnot cycle between the high (boiler out) temperature and the low (condenser out) tempreature')
	etaSecondLaw = F.Quantity(label = 'second law efficiency', description = 'ratio or real cycle efficiency over Carnot efficiency')
	efficiencyFieldGroup = F.FieldGroup([eta, etaCarnot, etaSecondLaw], 'Efficiency')
	resultEnergy = F.SuperGroup([flowFieldGroup, efficiencyFieldGroup], label = 'Energy')
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', resultEnergy])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#	def compute(self):
	def compute(self):
		# Connect components to points
		self.initCompute(self.fluidName, 4)
		self.pump.inlet = self.condenser.outlet = self.fp[0]
		self.pump.outlet = self.boiler.inlet = self.fp[1]
		self.boiler.outlet = self.turbine.inlet= self.fp[2]
		self.turbine.outlet = self.condenser.inlet = self.fp[3]

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
		self.pump.compute(self.pHigh)
		self.boiler.compute()	
		self.turbine.compute(self.pLow)
		self.condenser.compute()
		
	def postProcess(self):
		super(RankineCycle, self).postProcess(self.ambientTemperature)
		# Flows
		self.pumpPower = self.mDot * self.pump.w 
		self.boilerHeat = self.mDot * self.boiler.qIn
		self.turbinePower = - self.mDot * self.turbine.w
		self.condenserHeat = - self.mDot * self.condenser.qIn 
		# Efficiencies
		self.eta = (self.turbinePower - self.pumpPower) / self.boilerHeat
		self.etaCarnot = 1 - self.condenser.outlet.T / self.boiler.outlet.T
		self.etaSecondLaw = self.eta / self.etaCarnot
	
	def createStateDiagram(self):
		diagram = PHDiagram(self.fluidName, temperatureUnit = 'degC')
		diagram.setLimits()
		fig  = diagram.draw()
		ax = fig.get_axes()[0]
		
		ncp = len(self.fp)
		for i in range(ncp):
			ax.semilogy(self.fp[i].h/1e3, self.fp[i].p/1e5, 'ko')
			ax.semilogy(
				[self.fp[i].h/1e3, self.fp[(i + 1)%ncp].h/1e3], 
				[self.fp[i].p/1e5, self.fp[(i + 1)%ncp].p/1e5],
				'k', linewidth = 2)
			ax.annotate('{}'.format(i+1), 
				xy = (self.fp[i].h/1e3, self.fp[i].p/1e5),
				xytext = (10, 3), textcoords = 'offset points',
				size = 'x-large')
		fHandle, resourcePath  = diagram.export(fig)
		self.diagram = resourcePath
		os.close(fHandle)


class RankineCycleWithRecurperator(RankineCycle):
	label = "Rankine cycle with recurperator"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/RankineCycle.png",  height = 300)
	description = F.ModelDescription("Rankine cycle with recurperator, \
		using the temperature of the hot steam before the condenser to pre-heat the fluid before entering the boiler", show = True)
	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	recurperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recurperator')
	inputs = F.SuperGroup(['workingFluidGroup', 'pump', recurperator, 'boiler', 'turbine', 'condenser'])
	#--------------- Model view ---------------#

	#================ Results ================#
	#---------------- Energy flows -----------#
	recurperatorHeat = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'recurperator heat rate')
	flowFieldGroup = F.FieldGroup(['pumpPower', recurperatorHeat, 'boilerHeat', 'turbinePower', 'condenserHeat'], label = 'Energy flows')
	#================ Methods ================#
	def compute(self):
		# Connect components to points
		self.initCompute(self.fluidName, 6)
		self.pump.inlet = self.condenser.outlet = self.fp[0]
		self.pump.outlet = self.recurperator.inlet1 = self.fp[1]
		self.recurperator.outlet1 = self.boiler.inlet = self.fp[2]
		self.boiler.outlet = self.turbine.inlet= self.fp[3]
		self.turbine.outlet = self.recurperator.inlet2 = self.fp[4]
		self.recurperator.outlet2 = self.condenser.inlet = self.fp[5]

		# Cycle iterations
		absToleranceEnthalpy = 1.0;
		maxNumIter = 20
		i = 0
		self.fp[0].update_pq(self.pLow, 0)
		self.fp[4].update_pq(self.pLow, 1)
		while (i < maxNumIter):
			hOld = self.fp[0].h
			print hOld
			self.computeCycle()
			hNew = self.fp[0].h
			if (abs(hOld - hNew) < absToleranceEnthalpy):
				print hNew
				break
		if (hOld - hNew >= absToleranceEnthalpy):
			raise E.ConvergenceError('Solution did not converge')

		# Results
		self.postProcess()
		
	def computeCycle(self):
		self.pump.compute(self.pHigh)
		self.recurperator.compute(self.mDot, self.mDot)
		self.boiler.compute()	
		self.turbine.compute(self.pLow)
		self.condenser.compute()
		
	def postProcess(self):
		super(RankineCycleWithRecurperator, self).postProcess()
		# Flows
		self.recurperatorHeat = self.recurperator.QDot 
	
	def createStateDiagram(self):
		diagram = PHDiagram(self.fluidName, temperatureUnit = 'degC')
		diagram.setLimits()
		fig  = diagram.draw()
		ax = fig.get_axes()[0]
		
		ncp = len(self.fp)
		for i in range(ncp):
			ax.semilogy(self.fp[i].h/1e3, self.fp[i].p/1e5, 'ko')
			ax.semilogy(
				[self.fp[i].h/1e3, self.fp[(i + 1)%ncp].h/1e3], 
				[self.fp[i].p/1e5, self.fp[(i + 1)%ncp].p/1e5],
				'k', linewidth = 2)
			ax.annotate('{}'.format(i+1), 
				xy = (self.fp[i].h/1e3, self.fp[i].p/1e5),
				xytext = (3, 3), textcoords = 'offset points',
				size = 'x-large')
		fHandle, resourcePath  = diagram.export(fig)
		self.diagram = resourcePath
		os.close(fHandle)

if __name__ == '__main__':
	c1 = RankineCycle()
	c1.modelView2Json(c1.modelBlocks[0])
	