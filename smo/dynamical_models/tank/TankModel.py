'''
Created on March 28, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import pylab as plt

import smo.media.CoolProp as CP
import smo.dynamical_models.core as DMC
import smo.dynamical_models.thermofluids as DM
from smo.dynamical_models.thermofluids import Structures as DMS
from TankController import TankController as TC
from TankController import TankController
from smo.util import AttributeDict 

from assimulo.exception import TerminateSimulation
from smo.math.util import NamedStateVector

""" Global Settings """
import os
from SmoWeb.settings import MEDIA_ROOT
tmpFolderPath = os.path.join (MEDIA_ROOT, 'tmp')
csvFileName = os.path.join(tmpFolderPath, 'TankSimulations_TankModel_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'TankSimulations_SimulationResults.h5')
dataStorageDatasetPath = '/TankModel'


class TankModel(DMC.Simulation):
	name = 'Model of a tank fueling and extraction'
	
	def __init__(self, params = None, **kwargs):
		super(TankModel, self).__init__(**kwargs)
		if params == None:
			params = AttributeDict(kwargs)

		# Create state vector and derivative vector
		stateVarNames = ['WRealCompressor', 'TTank', 'rhoTank', 'TLiner_1', 'TLiner_2', 'TComp_1', 'TComp_2', 'TComp_3', 'TComp_4'] 
		self.y = NamedStateVector(stateVarNames)
		self.yRes = NamedStateVector(stateVarNames)
		self.yDot = NamedStateVector(stateVarNames)

		# Initialize storage
		self.resultStorage = DMC.ResultStorage(
			filePath = dataStorageFilePath,
			datasetPath = dataStorageDatasetPath)
		if (kwargs.get('initDataStorage', True)):
			self.resultStorage.initializeWriting(
				varList = ['t'] + stateVarNames + ['pTank', 'TCompressorOut', 'TConditionerOut'],
				chunkSize = 10000)

		# Fueling source
		self.fuelingSource = DM.FluidStateSource(params.fuelingSource)
		self.fuelingSource.initState(params.fuelingSource)
		
		# Compressor	
		self.compressor = DM.Compressor(params.compressor)
		# Connect the compressor to the fluid source
		self.compressor.portIn.connect(self.fuelingSource.port1)
		
		# Conditioner
		self.conditioner = DM.FluidHeater(params.conditioner)
		self.conditioner.setEffectivnessModel(epsilon = params.conditioner.epsilon)
		# Connect the conditioner to the compressor
		self.conditioner.portIn.connect(self.compressor.portOut)
		# Connect the conditioner to the heater (i.e. temperature source)
		self.conditionerHeater = DMS.ThermalPort('C', DMS.ThermalState(T = params.conditionerHeater.T))
		self.conditioner.thermalPort.connect(self.conditionerHeater)
		
		# Tank chamber
		self.tank = DM.FluidChamber(params.tank)
		self.tank.initialize(params.tank.TInit, params.tank.pInit)
		# Connect the tank to the conditioner
		self.tank.fluidPort.connect(self.conditioner.portOut)
		
		# Extraction sink
		self.extractionSink = DM.FlowSource(params.extractionSink)
		# Connect the extraction sink with the tank
		self.extractionSink.port1.connect(self.tank.fluidPort)
		
		# Tank convection component
		self.tankInternalConvection = DM.ConvectionHeatTransfer(params.tankInternalConvection)
		# Connect to the fluid in the tank
		self.tankInternalConvection.fluidPort.connect(self.tank.fluidPort)

		# Tank (Liner)
		self.liner = DM.SolidConductiveBody(params.liner)
		# Connect to the tank convection component
		self.tankInternalConvection.wallPort.connect(self.liner.port1)
		
		# Tank (composite)
		self.composite = DM.SolidConductiveBody(params.composite)
		# Connect the liner to the composite
		self.composite.port1.connect(self.liner.port2)
				
		# Ambient fluid component
		self.ambientSource = DM.FluidStateSource(params.ambientSource)
		self.ambientSource.initState(params.ambientSource)
		
		# Composite convection component
		self.tankExternalConvection = DM.ConvectionHeatTransfer(params.tankExternalConvection)
		# Connect the composite convection to the ambient fluid
		self.tankExternalConvection.fluidPort.connect(self.ambientSource.port1)
		# Connect the composite convection to the composite  
		self.tankExternalConvection.wallPort.connect(self.composite.port2)
		
		# Controller
		self.controller = params.controller
		
		# Initialize the state variables
		self.y.WRealCompressor = 0. # [W]
		self.y.TLiner_1 = self.liner.T[0]
		self.y.TLiner_2 = self.liner.T[1]
		self.y.TComp_1 = self.composite.T[0]
		self.y.TComp_2 = self.composite.T[1]
		self.y.TComp_3 = self.composite.T[2]
		self.y.TComp_4 = self.composite.T[3]
		self.y.TTank = self.tank.fState.T
		self.y.rhoTank = self.tank.fState.rho 
		
		# Set all the initial state values
		self.y0 = self.y.get(copy = True)
		
		# Set the initial flags
		self.sw0 = [True]
		
	def rhs(self, t, y, sw):
		# Compute the derivatives of the state variables
		self.compute(t, y, sw)
		
		# Return the derivatives
		self.yDot.WRealCompressor = self.compressor.WRealDot
		self.yDot.TTank = self.tank.TDot
		self.yDot.rhoTank = self.tank.rhoDot
		self.yDot.TLiner_1 = self.liner.TDot[0]
		self.yDot.TLiner_2 = self.liner.TDot[1]
		self.yDot.TComp_1 = self.composite.TDot[0]
		self.yDot.TComp_2 = self.composite.TDot[1]
		self.yDot.TComp_3 = self.composite.TDot[2]
		self.yDot.TComp_4 = self.composite.TDot[3]
		return self.yDot.get()
	
	def compute(self, t, y, sw = None):
		try:
			# Set the values (from the Solver) of the state variables
			self.y.set(y)
			
			# Set states of the components		
			self.tank.setState(self.y.TTank, self.y.rhoTank)
			self.liner.setState([self.y.TLiner_1, self.y.TLiner_2])
			self.composite.setState([self.y.TComp_1, self.y.TComp_2, self.y.TComp_3, self.y.TComp_4])
			self.conditioner.setState()
			

			# Compute derivatives of the state variables 
			# Compressor
			self.compressor.n = self.controller.outputs.nCompressor
			self.compressor.compute()
			# Conditioner
			self.conditioner.compute()
			# Extraction sink
			self.extractionSink.mDot = self.controller.outputs.mDotExtr
			self.extractionSink.compute()
			# Convection components
			self.tankInternalConvection.hConv = self.controller.outputs.hConvTank
			self.tankInternalConvection.compute()
			self.tankExternalConvection.compute()
			# Liner and composite
			self.composite.compute()
			self.liner.compute()
			# Tank
			self.tank.compute()
			
		except Exception, e:
			# Log the error if it happens in the compute() function
			print('Exception at time {}: {}'.format(t, e))
			raise e
	
	def state_events(self, t, y, sw):
		eventIndicators = np.ones(len(sw))
		self.compute(t, y, sw)
		self.controller.setInputs(pTank = self.tank.p)
		eventIndicators[0] = self.controller.checkForStateTransition()
		return eventIndicators
	
	def step_events(self, solver):
		# Called on each time step
		pass
	
	def handle_event(self, solver, eventInfo):
		reportEvents = False
		stateEventInfo, timeEvent = eventInfo
		# Handle time events
		if (timeEvent):
			timeEventList = self.processTimeEvent(solver.t)
			self.controller.processTimeEvent(timeEventList[0])
			if (reportEvents):
				print ("Time event '{}' located at time {}".format(solver.t, solver.sw))

		# Handle state events
		if (len(stateEventInfo) > 0):
			if (abs(stateEventInfo[0]) > 0.5):
				oldState = self.controller.state
				self.controller.makeStateTransition(solver)
				
				tWaitBeforeFueling = self.controller.parameters.tWaitBeforeFueling
				tWaitBeforeExtraction = self.controller.parameters.tWaitBeforeExtraction
				if (oldState == TC.EXTRACTION and tWaitBeforeFueling != 0.0):
					self.timeEventRegistry.add(DMC.TimeEvent(t = solver.t + tWaitBeforeFueling, eventType = TC.TE_BEGIN_FUELING, description = 'Begin fueling'))
				
				if (oldState == TC.FUELING and tWaitBeforeExtraction != 0.0):
					self.timeEventRegistry.add(DMC.TimeEvent(t = solver.t + tWaitBeforeExtraction, eventType = TC.TE_BEGIN_EXTRACTION, description = 'Begin extraction'))
				
			if (reportEvents):
				print ('State event located at time {}'.format(solver.t, solver.sw))
		
		if (False):
			raise TerminateSimulation()
	
	def handle_result(self, solver, t, y):
		super(TankModel, self).handle_result(solver, t, y)
		
		self.compute(t, y)		
		self.resultStorage.record[:] = (
			t, self.y.WRealCompressor,
			self.y.TTank, self.y.rhoTank, 
			self.y.TLiner_1, self.y.TLiner_2, 
			self.y.TComp_1, self.y.TComp_2, self.y.TComp_3, self.y.TComp_4, 
			self.tank.fState.p, self.compressor.TOut, self.conditioner.TOut)
		self.resultStorage.saveTimeStep()
		
	def loadResult(self, simIndex):
		self.resultStorage.loadResult(simIndex)
		
	def getResults(self):
		return self.resultStorage.data

	def plotHDFResults(self):
		data = self.resultStorage.data
		xData = data['t']
		plt.plot(xData, data['pTank']/1e5, 'g', label = 'tank pressure [bar]')
		plt.plot(xData, data['TTank'], 'r', label = 'tank temperature [K]')
		plt.plot(xData, data['TLiner_2'], 'm', label = 'tank liner temperature [K]')
		plt.plot(xData, data['TComp_4'], 'b', label = 'tank composite temperature [K]')	
		#plt.plot(xData, data['rhoTank'] * self.tank.V, 'm', label = 'tank mass [kg]')
		plt.plot(xData, data['TCompressorOut'], 'y', label = 'compressor outlet temperature of fluid [K]')
		plt.plot(xData, data['TConditionerOut'], 'm--', label = 'conditioner outlet temperature of fluid [K]')
		#plt.plot(xData, data['WRealCompressor']/1e3, 'y--', label = 'compressor real work [KW]')
		
		plt.gca().set_xlim([0, len(xData)])
		plt.legend()
		plt.show()
		
class TankModelFactory():
	@staticmethod
	def create(params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
		
		if params.conditioner.workingState == 0:
			params.conditioner.epsilon = 0.
		
		tankModel = TankModel(
			initDataStorage = True, 
			controller = TankController(
				initialState = params.controller.initialState, 
				tWaitBeforeExtraction = params.controller.tWaitBeforeExtraction, 
				tWaitBeforeFueling = params.controller.tWaitBeforeFueling,
				pMin = params.controller.pMin,
				pMax = params.controller.pMax,
				mDotExtr = params.controller.mDotExtr,
				hConvTankWaiting = params.tank.hConvInternalWaiting,
				hConvTankExtraction = params.tank.hConvInternalExtraction,
				hConvTankFueling = params.tank.hConvInternalFueling,
				nCompressor = params.controller.nCompressor,
			),
			fuelingSource = AttributeDict(
				fluid = params.fluid,
				sourceType = params.fuelingSource.sourceType,
				T = params.fuelingSource.T,
				p = params.fuelingSource.p,
				q = params.fuelingSource.q,
			),
			compressor = AttributeDict(
				fluid = params.fluid,
				etaS = params.compressor.etaS,
				fQ = params.compressor.fQ,
				V = params.compressor.V,
			),
							
			conditioner = AttributeDict(
				fluid = params.fluid,
				epsilon = params.conditioner.epsilon,
			),
			conditionerHeater = AttributeDict(
				T = params.conditioner.THeater,
			),
							
			tank = AttributeDict(
				fluid = params.fluid, 
				V = params.tank.volume,
				TInit = params.tank.TInit,
				pInit = params.tank.pInit,
			),
			tankInternalConvection = AttributeDict(
				A = params.tank.wallArea,
				hConv = 100., #TRICKY: unused parameter
			),
			liner = AttributeDict(
				material = params.tank.linerMaterial,
				mass = params.tank.linerMass,
				thickness = params.tank.linerThickness,
				conductionArea = params.tank.wallArea,
				port1Type = 'C',
				port2Type = 'C',
				numMassSegments = 2,
				TInit = params.tank.TInit,
			),
			composite = AttributeDict(
				material = params.tank.compositeMaterial, 
				mass = params.tank.compositeMass,
				thickness = params.tank.compositeThickness,
				conductionArea = params.tank.wallArea,
				port1Type = 'R', 
				port2Type = 'C', 
				numMassSegments = 4,
				TInit = params.tank.TInit
			),
			tankExternalConvection = AttributeDict(
				A = params.tank.wallArea,
				hConv = params.tank.hConvExternal,
			),	
			ambientSource = AttributeDict(
				fluid = params.ambientFluid,
				sourceType = DM.FluidStateSource.TP,
				T = params.TAmbient,
				p = 1.e5,
			),
			extractionSink = AttributeDict(
				fluid = params.fluid,
				mDot = 0.0, #TRICKY: unused parameter
				TOut = params.TAmbient, #TRICKY: unused parameter
			),
		)
		return tankModel
		
def testTankModel():
	print "=== BEGIN: testTankModel ==="
	# Settings
	simulate = True #True - run simulation; False - plot an old results
	
	# Create the model
	tankModel = TankModelFactory.create(
		fluid = CP.Fluid('ParaHydrogen'),
		ambientFluid = CP.Fluid('Air'),
		TAmbient = 288.15,
		
		controller = AttributeDict(
			initialState = TC.FUELING, 
			tWaitBeforeExtraction = 150., 
			tWaitBeforeFueling = 150.,
			pMin = 20e5,
			pMax = 300e5,
			mDotExtr = 30/3600.,
			nCompressor = 0.53 * 1.44,
		),
									
		fuelingSource = AttributeDict(
			sourceType = DM.FluidStateSource.PQ,
			T = 15, #:TRICKY: unused
			p = 2.7e5,
			q = 0.,
		),
															
		compressor = AttributeDict(
			etaS = 0.9,
			fQ = 0.,
			V = 0.5e-3,
		),

		conditioner = AttributeDict(
			workingState = 1,
			epsilon = 1.0,
			THeater = 300,
		),

		tank = AttributeDict(
 			wallArea = 1.8,
 			volume = 0.1,
 			TInit = 300.,
			pInit = 20e5,
			linerMaterial = 'Aluminium6061',
			linerMass = 24., #:TODO: calculate from wall area and thickness
		    linerThickness = 0.004,
		    compositeMaterial = 'CarbonFiberComposite',
		    compositeMass = 34., #:TODO: calculate from wall area and thickness
			compositeThickness = 0.0105,
			hConvExternal = 100.,
			hConvInternalWaiting = 10.,
			hConvInternalExtraction = 20.,
			hConvInternalFueling = 100.,
 		),
	)
	
	# Run simulation or load old results
	if (simulate):
		tankModel.prepareSimulation()
		tankModel.run(tFinal = 2000., tPrint = 1.0)
	else:
		tankModel.loadResult(simIndex = 1)
	
	# Export to csv file
	#tankModel.resultStorage.exportToCsv(fileName = csvFileName)
	
	# Plot results 
	tankModel.plotHDFResults()
	
	print "=== END: testTankModel ==="
	
if __name__ == '__main__':
	testTankModel()
