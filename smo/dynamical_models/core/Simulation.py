'''
Created on Mar 8, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import h5py
from blist import sortedlist
from assimulo.solvers import CVode
from assimulo.problem import Explicit_Problem
from smo.util import AttributeDict
from smo.data.util import genTimestampUUID

class TimeEvent(object):
	def __init__(self, t, eventType, description = None):
		self.t = t
		self.eventType = eventType
		self.description = description
	def __str__(self):
		return self.description

class ResultStorage(object):
	def __init__(self, filePath, datasetPath):
		"""
		Writes and reads simulation results from HDF file
		"""
		self.filePath = filePath
		self.h5File = h5py.File(filePath, 'a')
		self.datasetPath = datasetPath
	
	def initializeWriting(self, varList, chunkSize):
		# Size of result chunks
		self.chunkSize = int(chunkSize)
		# Create the group for the result if not present
		if (self.datasetPath not in self.h5File):
			self.h5File.create_group(self.datasetPath)
		self.simulationName = genTimestampUUID()
		# Create column type
		dtype = self.makeDType(varList = varList)
		# Create numpy array used as a buffer for writing
		self.buffer = np.zeros(shape = (self.chunkSize), dtype = dtype)
		# Create the raw result dataset
		self.data = self.h5File[self.datasetPath].create_dataset(
					self.simulationName + '_raw', shape = (0,), dtype = dtype,
					chunks = (self.chunkSize,), maxshape = (None,))
		# Create a lenngth 1 array for storing the current values for the time step
		self.record = np.empty(shape = (1,), dtype = dtype)
		self.bufferIndex = 0

	def makeDType(self, varList):
		dtype = [(name, np.float32) for name in varList]
		return dtype
	
	def saveTimeStep(self):
		# Save the current time step
		self.buffer[self.bufferIndex] = self.record
		self.bufferIndex += 1
		# If the buffer is full dump it to the result file
		if (self.bufferIndex >= self.chunkSize):
			#print ('Wrote the buffer to HDF')
			self.data.resize((len(self.data) + self.chunkSize,))
			self.data[-self.chunkSize:] = self.buffer
			self.bufferIndex = 0
		
	def finalizeResult(self):
		# Dump what is left in the buffer to the raw dataset
		if self.bufferIndex > 0:
			self.data.resize((len(self.data) + self.bufferIndex,))
			self.data[-self.bufferIndex:] = self.buffer[:self.bufferIndex]
		
		# Create the processed data set
		self.h5File[self.datasetPath].create_dataset(self.simulationName, 
				data = self.data, compression="gzip")
		# Delete the raw data dataset
		del self.h5File[self.datasetPath][self.simulationName + '_raw']
		# Assign the new dataset to the data variable 
		self.data = self.h5File[self.datasetPath][self.simulationName]
		self.h5File.flush()
		self.h5File.close()
	
	def openStorage(self):
		self.h5File = h5py.File(self.filePath, 'r')
	
	def closeStorage(self):
		self.h5File.close()
	
	def loadResult(self):
		return self.h5File[self.datasetPath][self.simulationName]
	
	def exportToCsv(self, fileName, tPrint = None):
		f = open(fileName, 'w')
		f.write(",".join(self.data.dtype.names))
		f.write('\n')
		if (tPrint is None):
			for row in self.data:
				f.write(",".join(["{}".format(value) for value in row]))
				f.write('\n')
		else:
			# Here the resampling code should be added
			pass
		f.close()
	
class Simulation(Explicit_Problem):
	def __init__(self, **kwargs):
		self.timeEventRegistry = sortedlist(key=lambda x: x.t)
	
	def time_events(self, t, y, sw):
		if (len(self.timeEventRegistry) > 0):
			if (self.timeEventRegistry[0].t < t):
				j = 0
				while j < len(self.timeEventRegistry):
					if (self.timeEventRegistry[j].t < t):
						j += 1
					else:
						break
				del self.timeEventRegistry[:j]
			return self.timeEventRegistry[0].t
	
	def processTimeEvent(self, t):
		dt = 1e-6
		j = 0
		while j < len(self.timeEventRegistry):
			if (self.timeEventRegistry[j].t < t + dt):
				j += 1
			else:
				break
		timeEventList = self.timeEventRegistry[:j]
		del self.timeEventRegistry[:j]
		return timeEventList

	def prepareSimulation(self):
		#Define an explicit solver 
		simSolver = CVode(self) 
		#Create a CVode solver
		#Sets the parameters 
		#simSolver.verbosity = LOUD
		simSolver.report_continuously = True
		simSolver.iter = 'Newton' #Default 'FixedPoint'
		simSolver.discr = 'BDF' #Default 'Adams'
		#simSolver.discr = 'Adams' 
		simSolver.atol = [1e-6]	#Default 1e-6 
		simSolver.rtol = 1e-6 	#Default 1e-6
		simSolver.problem_info['step_events'] = True # activates step events
		#simSolver.maxh = 1.0
		simSolver.store_event_points = True
		self.simSolver = simSolver
		
	def run(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
		
		# Remember the final time
		self.tFinal = params.tFinal
		
		# Run simulation		
		self.simSolver.simulate(
			tfinal = params.tFinal, 
			ncp = np.floor(params.tFinal/params.tPrint)
		)
		self.resultStorage.finalizeResult()
