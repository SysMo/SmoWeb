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

class TimeEvent(object):
	def __init__(self, t, eventType, description = None):
		self.t = t
		self.eventType = eventType
		self.description = description
	def __str__(self):
		return self.description
	
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

	def makeDType(self, varList):
		dtype = [(name, np.float32) for name in varList]
		return dtype

	def initDataStorage(self, varList):
		# Data storage:
		self.fRes = h5py.File('../../data/results.h5')
		if ('cycles' not in self.fRes):
			self.fRes.create_group('cycles')
			self.fRes['cycles'].attrs['i'] = 0
		simNum = self.fRes['cycles'].attrs['i'] + 1
		self.fRes['cycles'].attrs['i'] = simNum
		self.storageDType = self.makeDType(varList = varList)
		self.simulationName = 'simulation_{:0>4d}'.format(simNum)
		resStorage = self.fRes['cycles'].create_dataset(self.simulationName + '_raw', shape = (0,), dtype = self.storageDType,
					chunks = (10000,), maxshape = (None,))	
		resStorage.attrs['len'] = 0
		self.resRecord = np.empty(shape = (1,), dtype = self.storageDType)
		self.resLen = 0
		self.lastStorage = -1.
		self.resStorage = resStorage
	
	def saveTimeStep(self):
		if (self.resLen >= len(self.resStorage)):
			self.resStorage.resize((len(self.resStorage) + 10000,))
		t = self.resRecord['t'][0]
		if ( t - self.lastStorage > 1e-3 and t > 1e-10):
			self.resStorage[self.resLen] = self.resRecord
			self.lastStorage = t
			self.resLen += 1
			self.resStorage.attrs['len'] = self.resLen
		else:
			self.resStorage[self.resLen - 1] = self.resRecord
		
	def finalizeResult(self):
		res = self.resStorage[:self.resLen]
		del self.fRes['cycles'][self.simulationName + '_raw']
		self.fRes['cycles'].create_dataset(self.simulationName, data = res, compression="gzip")
		self.resStorage = self.fRes['cycles'][self.simulationName]
		self.fRes.flush()
	
	def loadResult(self, filePath, datasetPath):
		hdfFile = h5py.File(filePath)		
		self.resStorage = hdfFile[datasetPath]
	
	def exportToCsv(self, fileName = '../../data/SimulationResult.csv'):
		f = open(fileName, 'w')
		f.write(",".join(self.resStorage.dtype.names))
		f.write('\n')
		for row in self.resStorage:
			f.write(",".join(["{}".format(value) for value in row]))
			f.write('\n')
		f.close()

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
