'''
Created on Nov 09, 2014
@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
from smo.web.modules import RestModule
import lib.ThermodynamicComponents as TC
from lib.CycleBases import HeatPumpCycle
import smo.web.exceptions as E 


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
	exampleAction = ServerAction("loadEg", label = "Examples", options = (
			('R134aCycle', 'Typical fridge with R134a as a refrigerant'),
			('CO2TranscriticalCycle', 'CO2 transcritial cycle'),
	))
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
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')

		self.initCompute(fluid = self.fluidName, numPoints = 4)
		self.evaporator.outlet = self.compressor.inlet = self.fp[0]
		self.compressor.outlet = self.condenser.inlet = self.fp[1]
		self.condenser.outlet = self.throttleValve.inlet = self.fp[2]
		self.throttleValve.outlet = self.evaporator.inlet = self.fp[3]
		
		# Initial guess
		self.fp[0].update_pq(self.pLow, 1)
		# Cycle iterations
		absToleranceEnthalpy = 1.0;
		maxNumIter = 20
		i = 0
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
		
		
	def postProcess(self):
		super(ReverseBraytonCycle, self).postProcess(self.TAmbient)
		self.compressorPower = self.mDotRefrigerant * self.compressor.w
		self.compressorHeat = -self.mDotRefrigerant * self.compressor.qIn
		self.condenserHeat = -self.mDotRefrigerant * self.condenser.qIn
		self.evaporatorHeat = self.mDotRefrigerant * self.evaporator.qIn
		
		self.COPCooling = self.evaporatorHeat / self.compressorPower
		self.COPHeating = self.condenserHeat / self.compressorPower


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
	
	def R134aCycle(self):
		self.fluidName = 'R134a'
		self.pHighMethod = 'P'
		self.pHigh = (10, 'bar')
		self.pLowMethod = 'T'
		self.TEvaporation = (-20, 'degC')
		self.compressor.eta = 0.75
		self.compressor.fQ = 0.0
		self.condenser.computeMethod = 'T'
		self.condenser.TOutlet = (36, 'degC')
		self.evaporator.computeMethod = 'Q'
		self.evaporator.qOutlet = 1.0

class ReverseBraytonCycleWithRecurperator(ReverseBraytonCycle):
	label = "Reverse Brayton cycle (recurperator)"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/ReverseBraytonCycle.svg")
	description = F.ModelDescription("Brayton cycle with a recurperator precooling the stream before the throttle valve, using the cold stream at the evaporator outlet", show = True)
	#================ Inputs ================#
	#---------------- Fields ----------------#
	recurperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recurperator')
	inputs = F.SuperGroup(['workingFluidGroup', 'compressor', recurperator, 'condenser', 'evaporator'], label = 'Cycle definition')
	#--------------- Model view ---------------#

	#================ Results ================#
	#---------------- Energy flows -----------#
	recurperatorHeat = F.Quantity('HeatFlowRate', default = (0, 'kW'), label = 'recurperator heat rate')
	flowFieldGroup = F.FieldGroup(['compressorPower', recurperatorHeat, 'condenserHeat', 'evaporatorHeat'], label = 'Energy flows')
	#================ Methods ================#
	def compute(self):
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')

		self.initCompute(fluid = self.fluidName, numPoints = 6)
		self.evaporator.outlet = self.recurperator.inlet1 = self.fp[0]
		self.recurperator.outlet1 = self.compressor.inlet = self.fp[1]
		self.compressor.outlet = self.condenser.inlet = self.fp[2]
		self.condenser.outlet = self.recurperator.inlet2 = self.fp[3]
		self.recurperator.outlet2 = self.throttleValve.inlet = self.fp[4]
		self.throttleValve.outlet = self.evaporator.inlet = self.fp[5]
		
		# Initial guess
		self.fp[0].update_pq(self.pLow, 1)
		if (self.cycleTranscritical):
			self.fp[3].update_Tp(1.05 * self.fluid.critical['T'], self.pHigh)
		else:
			self.fp[3].update_pq(self.pHigh, 0)
		# Cycle iterations
		absToleranceEnthalpy = 1.0;
		maxNumIter = 20
		i = 0
		while (i < maxNumIter):
			hOld = self.fp[0].h
			print hOld
			self.computeCycle()
			hNew = self.fp[0].h
			if (abs(hOld - hNew) < absToleranceEnthalpy):
				break
		if (hOld - hNew >= absToleranceEnthalpy):
			raise E.ConvergenceError('Solution did not converge')

		# Results
		self.postProcess()
	
	def computeCycle(self):
		self.recurperator.compute(self.mDotRefrigerant, self.mDotRefrigerant)
		print self.fp[0].getStateVarsAsDict()
		self.compressor.compute(self.pHigh)
		print self.fp[1].getStateVarsAsDict()
		self.condenser.compute()
		print self.fp[2].getStateVarsAsDict()
		self.throttleValve.compute(self.pLow)
		self.evaporator.compute()
		
		if (self.cycleTranscritical and self.condenser.computeMethod == 'dT'):
			raise ValueError('In transcritical cycle, condenser sub-cooling cannot be used as input')
	
	def postprocess(self):
		super(ReverseBraytonCycleWithRecurperator, self).postProcess(self.TAmbient)
		self.recurperatorHeat = self.recurperator.QDot
	
	def R134aCycle(self):
		super(ReverseBraytonCycleWithRecurperator, self).R134aCycle()
		self.recurperator.eta = 0.7
		
class HeatPumpDoc(RestModule):
	name = 'HeatPumpDoc'
	label = 'Heat Pump (Docs)'
	template = 'documentation/html/HeatPumpDoc.html'
		
if __name__ == '__main__':
	#IsentropicCompression.test()
	pass
