import numpy as np
import pylab as plt

import logging
appLogger = logging.getLogger('AppLogger')

class PercentileCalculator:
	def __init__(self, stressVector, numBins):
		self.stressVector = np.array(stressVector, dtype = np.float)
		self.globalMin = np.min(self.stressVector)
		self.globalMax = np.max(self.stressVector)
		#appLogger.info("Minimum stress %f"%self.globalMin)
		#appLogger.info("Maximum stress %f"%self.globalMax)

		self.numBins = numBins
		self.binWidth = (self.globalMax - self.globalMin) / (numBins - 1)
		self.binCenters = np.arange(numBins) * self.binWidth + self.globalMin

	def locateExtrema(self):
		"""
		This function finds local extrema. It searches for alternating minima and maxima.
		To eliminate noise, a treshold of `binWidth` is used. 
		"""
		# Create the arrays for storing the extrema positions and values 
		extremaIndices = np.zeros(len(self.stressVector), dtype = np.int)
		extremaValues = np.zeros(len(self.stressVector), dtype = np.float)
		lastMinIndex = 0
		lastMaxIndex = 0
		lastMinValue = np.Inf
		lastMaxValue = -np.Inf
		j = 1
		
		# Add the first point
		extremaIndices[0] = 0
		extremaValues[0] = self.stressVector[0]

		# Decide if we start searching for min or max
		i = 1
		while (abs(self.stressVector[i] - self.stressVector[0]) < self.binWidth):
			i += 1
		if (self.stressVector[i] > self.stressVector[0]):
			lookingForMaximum = True
		else:
			lookingForMaximum = False
		
		# Search in the internal points
		while (i < len(self.stressVector)):
			sp = self.stressVector[i]
			if (sp > lastMaxValue):
				lastMaxValue = sp
				lastMaxIndex = i
			if (sp < lastMinValue):
				lastMinValue = sp
				lastMinIndex = i

			if (lookingForMaximum):
				if (sp < lastMaxValue - self.binWidth):
					extremaValues[j] = lastMaxValue
					extremaIndices[j] = lastMaxIndex
					j += 1
					lastMinValue = sp
					lastMinIndex = i
					lookingForMaximum = False
			else:
				if (sp > lastMinValue + self.binWidth):
					extremaValues[j] = lastMinValue
					extremaIndices[j] = lastMinIndex
					j += 1
					lastMaxValue = sp
					lastMaxIndex = i
					lookingForMaximum = True
			i += 1
		
		# Add the last point
		extremaIndices[j] = (len(self.stressVector) - 1)
		extremaValues[j] = self.stressVector[-1]
		j += 1
		
		# Trim the arrays and convert them to percentiles
		self.extremaIndices = extremaIndices[:j]
		self.extremaValues = np.floor((extremaValues[:j] - self.globalMin) / self.binWidth + 0.5).astype(np.int)
		
	def plot(self):
		ax1 = plt.subplot(211)
		plt.plot(self.stressVector)
#		plt.plot(self.extremaIndices, self.extremaValues, 'o')
		plt.subplot(212, sharex = ax1)
		plt.plot(self.extremaIndices, self.extremaValues, '.-')
		plt.show()

	@staticmethod
	def test():
		stressVectors = [
			[1, 2, 1],			
			[1, 1, 2],
			[1, 2, 1, 2],
			[1, 2, 3, 4, 3, 2, 3, 4, 5, 6, 4, 3, 1, 5, 1, 7, 3, 4, 5, 6, 7, 8],
			[1, 2, 3, 2],
			[1, 2, 1, 0],
		]
		for v in stressVectors:
			print('===================')
			pc = PercentileCalculator(v, numBins = 100)
			print("Stresses:")
			print(v)
			pc.locateExtrema()
			print("Extrema indices")
			print(pc.extremaIndices)
			print("Extrema values")
			print(pc.extremaValues)

class RainflowCounter:
	def __init__(self, extremaValues, stressBins):
		self.extremaValues = extremaValues
		self.stressBins = stressBins
		self.numBins = len(stressBins)
		self.rainflowMatrix = np.zeros((self.numBins, self.numBins))
	
	def fillRainflowMatrix(self, inputData):
		residual = np.zeros(self.numBins)
		residualIndices = np.zeros(self.numBins)
		iz = 0
		ir = 1
		for dataIndex in range(len(inputData)):
			stressValue = inputData[dataIndex]
			repeat = True
			while (repeat):
				repeat = False
				if (iz > ir):
					secLastRes = residual[iz - 2]
					lastRes = residual[iz - 1]
					if (stressValue - lastRes) * (lastRes - secLastRes) >= 0:
						iz -=  1
						repeat = True
					elif (np.abs(stressValue - lastRes) >= np.abs(lastRes - secLastRes)):
						#appLogger.info ("At index %d: closed loop found from '%d' to '%d'"%(dataIndex, secLastRes, lastRes))
						self.rainflowMatrix[lastRes, secLastRes] += 1
						iz = iz -2
						repeat = True
				elif (iz == ir):
					lastRes = residual[iz - 1]
					if ((stressValue - lastRes) * lastRes) >= 0:
						iz -= 1
						repeat = True
					elif (np.abs(stressValue) > np.abs(lastRes)):
						ir += 1
			residual[iz] = stressValue
			residualIndices[iz] = dataIndex + 2
			iz += 1
		
		return residual[:iz-1], residualIndices[:iz-1]
	
	def computeMatrix(self):
		self.residual0, tmp = self.fillRainflowMatrix(self.extremaValues)
		
	def residualRepeatedRun(self):
		resLen0 = len(self.residual0)
		repeatedResidual = np.zeros(2 * resLen0)
		repeatedResidual[:resLen0] = self.residual0[:]
		repeatedResidual[resLen0:] = self.residual0[:]
		self.residual, tmp = self.fillRainflowMatrix(repeatedResidual)
	
	def plot(self):
		#appLogger.info(self.rainflowMatrix.max(), self.rainflowMatrix.shape)
		#plt.subplot(211)
		ax1 = plt.gca()
		rainflowMatrixMaskedArray = np.ma.array(self.rainflowMatrix)
		rainflowMatrixMasked = np.ma.masked_where(rainflowMatrixMaskedArray < 1.0 , rainflowMatrixMaskedArray)
		plottedImage = ax1.matshow(rainflowMatrixMasked)
		plt.colorbar(plottedImage)
		ax1.set_title('Rainflow Matrix')		
		#plt.subplot(212)
		#plt.plot(self.residual0, '.-')
		#plt.plot(self.residual, '.-')
		plt.show()

class DamageCalculator:
	def __init__(self, rainflowMatrix, stressBins):
		self.rainflowMatrix = rainflowMatrix

		diagMatrix = np.zeros(shape = self.rainflowMatrix.shape)
		# Amplitude is half the hysteresis range
		self.cycleAmplitudes = np.abs((diagMatrix + stressBins) - (diagMatrix + stressBins).T) / 2
		colMatrix = np.zeros(shape = self.rainflowMatrix.shape)
		colMatrix += stressBins		 
		self.meanStresses = (colMatrix + colMatrix.T)/2
		
	def setSNCurveParameters(self, S_E, N_E, k):
		self.S_E = S_E
		self.N_E = N_E
		self.k = k
		
	def applyOneParameterMeanStressCorrection(self, M):		
		correction = (self.meanStresses * M) * (self.meanStresses >= -self.cycleAmplitudes) + \
				(-self.cycleAmplitudes * M) * (self.meanStresses < -self.cycleAmplitudes)
		self.correctedCycleAmplitudes = self.cycleAmplitudes + correction
		
	def computeDamage(self):
		self.damageMagnitudes = 1 / self.N_E * (self.correctedCycleAmplitudes / self.S_E)**self.k
		self.damage = np.sum(self.damageMagnitudes * self.rainflowMatrix) 
		#appLogger.info(self.cycleAmplitudes.tolist())
		#appLogger.info(self.correctedCycleAmplitudes.tolist())
		#appLogger.info(self.rainflowMatrix)
		return self.damage

if __name__ == '__main__':
	PercentileCalculator.test()