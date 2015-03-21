'''
Created on March 08, 2015

@author: Milen Borisov
'''

import numpy as np
import pylab as plt
import os

from assimulo.exception import TerminateSimulation
from smo.dynamical_models.core.Simulation import Simulation, TimeEvent, ResultStorage
from smo.math.util import NamedStateVector
from SmoWeb.settings import MEDIA_ROOT

""" Global Settings """
tmpFolderPath = os.path.join (MEDIA_ROOT, 'tmp')
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_SimpleChemostat_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/SimpleChemostat'



""" Classes """
class SimpleChemostatTimeEvent(TimeEvent):	
	"""
	Class for time event of SimpleChemostatModel
	"""
	def __init__(self, t, newValue_D):
		self.t = t
		self.newValue_D = newValue_D
		
		self.eventType = "Chemostat_TIME_EVENT"
		self.description = "Change the dilution rate (D) to {0}".format(newValue_D)
		
class SimpleChemostat(Simulation):
	"""
	Class for implementation the model of simple chemostat 
	"""
	name = 'Model of a simple chemostat.'
	
	def __init__(self, **kwargs):
		super(SimpleChemostat, self).__init__(**kwargs)
		self.tFinal = kwargs.get('tFinal', 100.0)

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
		
		# Set parameter values
		self.m = kwargs.get('m', 3)
		self.K = kwargs.get('k', 3.67)
		self.S_in = kwargs.get('S_in', 2.2)
		self.X_in = kwargs.get('X_in', 0.0)
		self.gamma = kwargs.get('gamma', 1)
		
		# Register time event (changed of D)
		self.D_vals = kwargs.get('D_vals', np.array([[100, 1.0]]))
		D_val = self.D_vals[0]
		self.D = D_val[1]
		
		t_ChangedD = D_val[0]
		for i in range(len(self.D_vals)-1):
			self.D_val = self.D_vals[i+1]
			self.timeEventRegistry.add(SimpleChemostatTimeEvent(t = t_ChangedD, newValue_D = self.D_val[1]))
			t_ChangedD += self.D_val[0]
		
		# Set initial values of the states
		self.y.S = kwargs.get('S0', 0)
		self.y.X = kwargs.get('X0', 0.5)
				
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
		super(SimpleChemostat, self).handle_result(solver, t, y)
		
		self.yRes.set(y)
		self.resultStorage.record[:] = (t, self.yRes.S, self.yRes.X, self.D)
		self.resultStorage.saveTimeStep()
		
	def run(self, tPrint = 1.0):
		self.simSolver.simulate(tfinal = self.tFinal, ncp = np.floor(self.tFinal/tPrint))
		self.resultStorage.finalizeResult()
		
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



""" Test functions """
def TestSimpleChemostat():
	# Settings
	simulate = False #True - run simulation; False - plot an old results 
	tFinal = 500
	D_vals = np.array([[100, 1], [200, 0.5], [1e6, 1.1]])
	
	# Create the model
	model = SimpleChemostat(
		D_vals = D_vals,
		tFinal = tFinal, 
		initDataStorage = simulate)
	
	# Run simulation or load old results
	if (simulate == True):
		model.prepareSimulation()
		model.run(tPrint = 1.0)
	else:
		model.loadResult(simIndex = 1)
	
	# Export to csv file
	model.resultStorage.exportToCsv(fileName = csvFileName)
	
	# Plot results
	model.plotHDFResults()
	plt.gca().set_xlim([0, model.tFinal])
	plt.legend()
	plt.show()
	
if __name__ == '__main__':
	#NamedStateVector.test()
	TestSimpleChemostat()
	