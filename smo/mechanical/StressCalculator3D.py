import numpy as np
import h5py

import logging
appLogger = logging.getLogger('AppLogger')	

""" Private: Settings """
stressTypeNames = ['s11', 's22', 's33', 's12', 's13', 's23']

class StressCalculator3D(object):
	def __init__(self, stressTablesPath, useCompiledExtensions = True):
		self.useCompiledExtensions = useCompiledExtensions
		self.createInterpFunctions(stressTablesPath)
				
	def createInterpFunctions(self, stressTablesPath):
		if self.useCompiledExtensions:
			from smo_ext.Math import Interpolator2D
		else:
			from smo.math.Interpolators import Interpolator2D
		# Create stress interpolators
		h5File = h5py.File(stressTablesPath)
		self.channelNames = [str(grp) for grp in h5File]
		
		self.stressInterpolators = {}
		for channelName in self.channelNames:
			appLogger.info("Creating interpolators for channel '%s'"%(channelName))
			TArr = np.array(h5File['/%s/T'%channelName])
			pArr = np.array(h5File['/%s/p'%channelName])
			self.stressInterpolators[channelName] = {}
			for stressTypeName in stressTypeNames:
				# Read stress data from hdf5 StressTables
				stressMatrix = np.array(h5File['/%s/%s'%(channelName, stressTypeName)])
				
				# Create stress interpolator function
				fInterp = Interpolator2D(TArr, pArr, stressMatrix)
	
				self.stressInterpolators[channelName][stressTypeName] = fInterp	
		h5File.close()
		
	def computeStresses(self, pData, TData):
		numbMeasurments = len(pData) #number measurements
		stressDType = [(channel, np.float64, (3, 3)) for channel in self.channelNames]
		self.stressData = np.zeros(shape = (numbMeasurments), dtype = stressDType)
		
		for channelName in self.channelNames:
			channelData = self.stressData[channelName]
			channelData[:, 0, 0] = self.stressInterpolators[channelName]['s11'](TData, pData)
			channelData[:, 1, 1] = self.stressInterpolators[channelName]['s22'](TData, pData)
			channelData[:, 2, 2] = self.stressInterpolators[channelName]['s33'](TData, pData)
			channelData[:, 0, 1] = channelData[:, 1, 0] = self.stressInterpolators[channelName]['s12'](TData, pData)
			channelData[:, 0, 2] = channelData[:, 2, 0] = self.stressInterpolators[channelName]['s13'](TData, pData)
			channelData[:, 1, 2] = channelData[:, 2, 1] = self.stressInterpolators[channelName]['s23'](TData, pData)
		
	def writeStresses(self, filePath, datasetName):
		h5File = h5py.File(filePath)
		appLogger.info('Writing stress dataset "%s" to file %s'%(datasetName, filePath))
		if datasetName in h5File:
			appLogger.warning('Overwriting result stress "%s"'%datasetName)
			del h5File[datasetName]
		h5File.create_dataset(datasetName, data = self.stressData, chunks=True, compression="gzip")
		h5File.close()
