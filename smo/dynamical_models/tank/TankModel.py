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
	name = 'Model of a tank refueling and extraction'
	
	def __init__(self, params = None, **kwargs): #:TODO: params
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
				varList = ['t'] + stateVarNames + ['pTank', 'TCompressorOut'],
				chunkSize = 10000)

		# Fluid
		fluid = CP.Fluid('ParaHydrogen')

		# Refueling source
		self.refuelingSource = DM.FluidStateSource(fluid = fluid)
		self.refuelingSource.setState(params.refuelingSource)
		self.refuelingSource.compute()
		
		# Compressor	
		self.compressor = DM.Compressor(fluid = fluid, etaS = 0.9, fQ = 0., V = 0.5e-3)
		# Connect the compressor to the fluid source
		self.compressor.portIn.connect(self.refuelingSource.port1)
		
		# Tank chamber
		self.tank = DM.FluidChamber(
			fluid = fluid, 
			V = 0.1155 #[m**3]
		)
		self.tank.initialize(
			300.0, #[K] 
			20e5, #[Pa]
		)
		# Connect the tank to the compressor
		self.tank.fluidPort.connect(self.compressor.portOut)
		
		# Extraction sink
		self.extractionSink = DM.FlowSource(fluid = fluid, mDot = 0.0, TOut = params.TAmbient)
		# Connect the extraction sink with the tank
		self.extractionSink.port1.connect(self.tank.fluidPort)
		
		# Tank convection component
		self.wallArea = 1.8 #[m**2]
		self.tankConvection = DM.ConvectionHeatTransfer(hConv = 100., A = self.wallArea)
		# Connect to the fluid in the tank
		self.tankConvection.fluidPort.connect(self.tank.fluidPort)

		# Tank (Liner)
		self.liner = DM.SolidConductiveBody(
			material = 'Aluminium6061', 
			mass = 24., #[kg]
			thickness = 0.004, #[m]
			conductionArea = self.wallArea, #[m**2]
			port1Type = 'C', port2Type = 'C', 
			numMassSegments = 2, 
			TInit = 300.0 #[K]
		)
		# Connect to the tank convection component
		self.tankConvection.wallPort.connect(self.liner.port1)
		
		# Tank (composite)
		self.composite = DM.SolidConductiveBody(
			material = 'CarbonFiberComposite', 
			mass = 34., #[kg]
			thickness = 0.0105, #[m]
			conductionArea = self.wallArea, #[m**2]
			port1Type = 'R', port2Type = 'C', 
			numMassSegments = 4,
			TInit = 300.0 #[K]
		)
		# Connect the liner to the composite
		self.composite.port1.connect(self.liner.port2)
				
		# Ambient fluid component
		ambientFluid = CP.Fluid('Air')
		ambientSource =DM.FluidStateSource(fluid = ambientFluid, sourceType = DM.FluidStateSource.TP)
		ambientSource.setState(sourceType = DM.FluidStateSource.TP, T = params.TAmbient, p = 1e5)
		ambientSource.compute()
		
		# Composite convection component
		self.compositeConvection = DM.ConvectionHeatTransfer(hConv = 100., A = self.wallArea)
		# Connect the composite convection to the ambient fluid
		self.compositeConvection.fluidPort.connect(ambientSource.port1)
		# Connect the composite convection to the composite  
		self.compositeConvection.wallPort.connect(self.composite.port2)
		
		# Controller
		self.controller = params.controller
		
		# Initialize the state variables
		self.y.WRealCompressor = 0. # [W]
		self.y.TLiner_1 = 300.0 #[K]
		self.y.TLiner_2 = 300.0 #[K]
		self.y.TComp_1 = 300.0 #[K]
		self.y.TComp_2 = 300.0 #[K]
		self.y.TComp_3 = 300.0 #[K]
		self.y.TComp_4 = 300.0 #[K]
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

			# Compute derivatives of the state variables 
			# Compressor
			self.compressor.n = self.controller.outputs.nCompressor
			self.compressor.compute()
			# Extraction sink
			self.extractionSink.mDot = self.controller.outputs.mDotExtr
			self.extractionSink.compute()
			# Convection components
			self.tankConvection.hConv = self.controller.outputs.hConvTank
			self.tankConvection.compute()
			self.compositeConvection.compute()
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
				
				tWaitBeforeRefueling = self.controller.parameters.tWaitBeforeRefueling
				tWaitBeforeExtraction = self.controller.parameters.tWaitBeforeExtraction
				if (oldState == TC.EXTRACTION and tWaitBeforeRefueling != 0.0):
					self.timeEventRegistry.add(DMC.TimeEvent(t = solver.t + tWaitBeforeRefueling, eventType = TC.TE_BEGIN_REFUELING, description = 'Begin refueling'))
				
				if (oldState == TC.REFUELING and tWaitBeforeExtraction != 0.0):
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
			self.tank.fState.p, self.compressor.TOut)
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
		plt.plot(xData, data['WRealCompressor']/1e3, 'y--', label = 'compressor real work [KW]')
		
		plt.gca().set_xlim([0, len(xData)])
		plt.legend()
		plt.show()	


def testTankModel():
	print "=== BEGIN: testTankModel ==="
	# Settings
	simulate = True #True - run simulation; False - plot an old results 
	
	# Create the controller
	controller = TankController(
		initialState = TC.REFUELING, 
		tWaitBeforeExtraction = 150., 
		tWaitBeforeRefueling = 150.,
		pMin = 20e5,
		pMax = 300e5,
		mDotExtr = 30/3600.,
		hConvTankWaiting = 10.,
		hConvTankExtraction = 20.,
		hConvTankRefueling = 100.,
		nCompressor = 0.53 * 1.44
	)
	
	# Create the model	
	class RefuelingSourceParams():
		sourceType = DM.FluidStateSource.PQ
		p = 2.7e5 #[Pa]
		q = 0. #[-]
							
	tankModel = TankModel(
		initDataStorage = simulate, 
		TAmbient = 288.15,
		controller = controller,
		refuelingSource = RefuelingSourceParams(),
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
