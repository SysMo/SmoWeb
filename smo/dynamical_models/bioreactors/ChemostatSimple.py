'''
Created on March 08, 2015

@author: Milen Borisov
'''
import numpy as np
import pylab as plt

from smo.util import AttributeDict 
from assimulo.exception import TerminateSimulation
from smo.dynamical_models.core.Simulation import Simulation, TimeEvent, ResultStorage
from smo.math.util import NamedStateVector

""" Global Settings """
import os
from SmoWeb.settings import MEDIA_ROOT
tmpFolderPath = os.path.join (MEDIA_ROOT, 'tmp')
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_ChemostatSimple_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/ChemostatSimple'


class ChemostatSimpleTimeEvent(TimeEvent):	
	"""
	Class for time event of ChemostatSimple
	"""
	def __init__(self, t, newValue_D):
		self.t = t
		self.newValue_D = newValue_D
		
		self.eventType = "Chemostat_TIME_EVENT"
		self.description = "Change the dilution rate (D) to {0}".format(newValue_D)
		
class ChemostatSimple(Simulation):
	"""
	Class for implementation the model of a simple chemostat 
	"""
	name = 'Model of a simple chemostat.'
	
	def __init__(self, params = None, **kwargs):
		super(ChemostatSimple, self).__init__(**kwargs)
		if params == None:
			params = AttributeDict(kwargs)
					
		# Initialize parameters
		self.m = params.m
		self.K = params.K
		self.S_in = params.S_in
		self.X_in = params.X_in
		self.gamma = params.gamma
		self.D_vals = params.D_vals

		# Create state vector and derivative vector
		stateVarNames = ['S', 'X'] 
		self.y = NamedStateVector(stateVarNames)
		self.yRes = NamedStateVector(stateVarNames)
		self.yDot = NamedStateVector(stateVarNames)

		# Initialize data storage
		self.resultStorage = ResultStorage(filePath = dataStorageFilePath,
										datasetPath = dataStorageDatasetPath)
		if (kwargs.get('initDataStorage', True)):
			self.resultStorage.initializeWriting(
				varList = ['t'] + stateVarNames + ['D'],
				chunkSize = 1e4)
		
		# Register time event (changed of D)
		D_val = self.D_vals[0]
		self.D = D_val[1]
		
		tChangedD = D_val[0]
		for i in range(len(self.D_vals)-1):
			self.D_val = self.D_vals[i+1]
			self.timeEventRegistry.add(ChemostatSimpleTimeEvent(t = tChangedD, newValue_D = self.D_val[1]))
			tChangedD += self.D_val[0]
		
		# Set initial values of the states
		self.y.S = params.S0
		self.y.X = params.X0
				
		# Set all the initial state values
		self.y0 = self.y.get(copy = True)
		
		# Set the initial flags
		self.sw0 = [True]
		
	def mu(self, S):
		return self.m * S / (self.K + S)
		
	def rhs(self, t, y, sw):
		# Set state values
		self.y.set(y)
		
		try:
			# Get state values
			S = self.y.S
			X = self.y.X
			
			# Compute state derivatives
			S_dot = (self.S_in - S)*self.D - (1/self.gamma)*self.mu(S)*X
			X_dot = (self.X_in - X)*self.D + self.mu(S)*X
			
		except Exception, e:
			self.resultStorage.finalizeResult()
			# Log the error if it happens in the rhs() function
			print("Exception at time {}: {}".format(t, e))
			raise e
			
		self.yDot.S = S_dot
		self.yDot.X = X_dot
		return self.yDot.get()
	
	
	def state_events(self, t, y, sw):
		eventIndicators = np.ones(len(sw))
		return eventIndicators
	
	def step_events(self, solver):
		# Called on each time step
		pass
	
	def handle_event(self, solver, eventInfo):
		reportEvents = True
		_stateEventInfo, timeEvent = eventInfo
		
		# Handle time events
		if (timeEvent):
			timeEventList = self.processTimeEvent(solver.t)
			self.D = timeEventList[0].newValue_D
			if (reportEvents):
				print("Time event located at time: {} - {}".format(solver.t, timeEventList[0].description))
	
		if (False):
			raise TerminateSimulation()
	
	def handle_result(self, solver, t, y):
		super(ChemostatSimple, self).handle_result(solver, t, y)
		
		self.yRes.set(y)
		self.resultStorage.record[:] = (t, self.yRes.S, self.yRes.X, self.D)
		self.resultStorage.saveTimeStep()
		
	def getResults(self):
		return self.resultStorage.data
	
	def loadResult(self, simIndex):
		self.resultStorage.loadResult(simIndex)
	
	def plotHDFResults(self):		
		data = self.resultStorage.data
		xData = data['t']
		plt.plot(xData, data['S'], 'r', label = 'S')
		plt.plot(xData, data['X'], 'b', label = 'X')
		plt.plot(xData, data['D'], 'g', label = 'D')
		
		plt.gca().set_xlim([0, len(xData) - 1])
		plt.legend()
		plt.show()


def TestChemostatSimple():
	print "=== BEGIN: TestChemostatSimple ==="
	
	# Settings
	simulate = True #True - run simulation; False - plot an old results 
	
	# Initialize simulation parameters
	solverParams = AttributeDict({
		'tFinal' : 500., 
		'tPrint' : 1.0
	})
		
	# Initialize model parameters
	modelParams = AttributeDict({
		'm' : 3.0,
		'K' : 3.7,
		'S_in' : 2.2,
		'X_in' : 0.0,
		'gamma' : 0.6,
		'D_vals' : np.array([[100, 1], [200, 0.5], [1e6, 1.1]]),
		'S0' : 0.0,
		'X0' : 0.5
	})
	
	# Create the model
	chemostat = ChemostatSimple(modelParams, initDataStorage = simulate)
	
	# Run simulation or load old results
	if (simulate == True):
		chemostat.prepareSimulation()
		chemostat.run(solverParams)
	else:
		chemostat.loadResult(simIndex = 1)
	
	# Export to csv file
	chemostat.resultStorage.exportToCsv(fileName = csvFileName)
	
	# Plot results
	chemostat.plotHDFResults()
	
	print "=== END: TestChemostatSimple ==="
	
	
if __name__ == '__main__':
	TestChemostatSimple()