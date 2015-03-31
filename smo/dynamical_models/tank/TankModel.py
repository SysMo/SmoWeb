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
	name = 'Model of the tank (refueling & extraction)'
	
	def __init__(self, controller, **kwargs):
		super(TankModel, self).__init__(**kwargs)
		self.tFinal = kwargs.get('tFinal', 100.0)

		# Create state vector and derivative vector
		stateVarNames = ['WRealCompressor', 'TTank', 'rhoTank', 'TLiner_1', 'TLiner_2', 'TComp_1', 'TComp_2', 'TComp_3', 'TComp_4'] 
		self.y = NamedStateVector(stateVarNames)
		self.yRes = NamedStateVector(stateVarNames)
		self.yDot = NamedStateVector(stateVarNames)

		# Initialize storage
		self.resultStorage = DMC.ResultStorage(
			filePath = dataStorageFilePath,
			datasetPath = dataStorageDatasetPath)
		if (kwargs.get('initDataStorage', False)):
			self.resultStorage.initializeWriting(
				varList = ['t'] + stateVarNames + ['pTank', 'TCompressorOut'],
				chunkSize = 10000)
		
		# Set some parameters
		self.mDotExtrModel = lambda t: -10./3600 if self.controller.state == TC.EXTRACTION else 0.
		TAmbient = kwargs.get('TAmbient', 288.15) #[K]
		if (hasattr(self, 'initialValues')):
			TTankInit = self.initialValues['TTank']
			pTankInit = self.initialValues['PTank']
			TCompositeInit = self.initialValues['TComposite']
		else:
			TTankInit = kwargs.get('TTankInit', 300.0) #[K]
			pTankInit = kwargs.get('pTankInit', 20e5) #[Pa]
			TCompositeInit = kwargs.get('TComposite', 300.0) #[K]

		# Fluid
		fluid = CP.Fluid(kwargs.get('fluid', 'ParaHydrogen'))

		# Refueling source
		self.refuelingSource = DM.FluidStateSource(fluid = fluid, sourceType = DM.FluidStateSource.PQ)
		self.refuelingSource.pIn = 2.7e5 #[Pa]
		self.refuelingSource.qIn = 0. #[-]
		self.refuelingSource.computeState()
		
		# Compressor	
		self.compressor = DM.Compressor(fluid = fluid, etaS = 0.9, fQ = 0., V = 0.5e-3)
		# Connect the compressor to the fluid source
		self.compressor.portIn.connect(self.refuelingSource.port1)
		
		# Tank chamber
		self.tank = DM.FluidChamber(
			fluid = fluid, 
			V = kwargs.get('V', 0.1155) #[m**3]
		)
		self.tank.initialize(TTankInit, pTankInit)
		# Connect the tank to the compressor
		self.tank.fluidPort.connect(self.compressor.portOut)
		
		# Extraction sink
		self.extractionSink = DM.FlowSource(fluid = fluid, mDot = 0.0, TOut = TAmbient)
		# Connect the extraction sink with the tank
		self.extractionSink.port1.connect(self.tank.fluidPort)
		
		# Tank convection component
		self.wallArea = kwargs.get('wallArea', 1.8) #[m**2]
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
			TInit = TTankInit #[K]
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
			TInit = TTankInit #[K]
		)
		# Connect the liner to the composite
		self.composite.port1.connect(self.liner.port2)
		# Outer composite side		
		self.composite.port2.connect(DMS.ThermalPort('R', DMS.HeatFlow(qDot = 0.)))
		
		# Controller
		self.controller = controller
		
		# Initialize the state variables
		self.y.WRealCompressor = 0. # [W]
		self.y.TLiner_1 = TTankInit
		self.y.TLiner_2 = TTankInit
		self.y.TComp_1 = TCompositeInit
		self.y.TComp_2 = TCompositeInit
		self.y.TComp_3 = TCompositeInit
		self.y.TComp_4 = TCompositeInit
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
			# Compressor (Refueling)
			self.compressor.n = self.controller.outputs.nPump
			self.compressor.compute()
			# Extraction sink
			self.extractionSink.mDot = self.mDotExtrModel(t)
			self.extractionSink.compute()
			# Convection components
			self.tankConvection.hConv = self.controller.outputs.hConvTank
			self.tankConvection.compute()
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
			# TODO process all time events if more than one present
			self.controller.processTimeEvent(timeEventList[0])
			if (reportEvents):
				print ("Time event '{}' located at time {}".format(solver.t, solver.sw))

		# Handle state events
		if (len(stateEventInfo) > 0):
			if (abs(stateEventInfo[0]) > 0.5):
				self.controller.makeStateTransition(solver)
				self.rhs(solver.t, solver.y, solver.sw)

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
		
	def run(self, tPrint = 1.0):
		self.simSolver.simulate(
			tfinal = self.tFinal, 
			ncp = np.floor(self.tFinal/tPrint)
		)
		self.resultStorage.finalizeResult()

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
	controller = TC(initialState = TC.REFUELING)
	model = TankModel(tFinal = 2000., initDataStorage = True, controller = controller)
	model.prepareSimulation()
	model.run(tPrint = 1.0)
	model.resultStorage.exportToCsv(fileName = csvFileName)
	model.plotHDFResults()
	
if __name__ == '__main__':
	testTankModel()
