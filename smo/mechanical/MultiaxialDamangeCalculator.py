'''
Created on Apr 20, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import os, glob
import numpy as np
import math as m
import h5py
from smo.util.log import SimpleAppLoggerConfgigurator
from smo.math.util import RecArrayManipulator
from smo.mechanical.StressCalculator3D import StressCalculator3D
from StressTensorCalculator import StressTensorCalculator as STC
import smo_ext.Mechanical as Mech

import logging
appLogger = logging.getLogger('AppLogger')

class MultiaxialDamageCalculator(object):
	def __init__(self, SNCurveParameters, numStressBins = 100, meanStressCorrectionFactor = 0.24, useCompiledExtensions = True):
		self.SNCurveParameters = SNCurveParameters
		self.numStressBins = numStressBins
		self.meanStressCorrectionFactor = meanStressCorrectionFactor
		self.useCompiledExtensions = useCompiledExtensions
		
	def scaleStresses(self, k = 2.0):
		if (self.useCompiledExtensions):
			# Allocate array for scaled stresses
			self.stressesScaled = self.stressSeries * 1.0
			Mech.scaleStressSeries_MultiaxialDamage(self.stressesScaled, k)
		else:
			# Allocate array for scaled stresses
			self.stressesScaled = self.stressSeries * 0
			numSamples = self.stressSeries.shape[0]
			# Min/max stress ratios
			V = np.ones(numSamples)
			for i in range(self.stressSeries.shape[0]):
				if (np.max(np.abs(self.stressSeries[i, :])) > 1e-8):
					#sPrincipal = np.zeros((3,), dtype = S.floatT)
					#sPrincipal = DC.computePrincipalStresses(self.stressSeries[i, :])
					sPrincipal = STC.computePrincipalStresses(self.stressSeries[i, :])
					if ((sPrincipal[0] <=  sPrincipal[1]) and (sPrincipal[1] <=  sPrincipal[2])):
						pass
					else:
						print sPrincipal 
					#err = np.abs(np.sum(sPrincipal - sPrincipalSeries[i, :]) / np.sum(sPrincipal))
					#if ( err > 1e-8):
					#	print ('Pricipal stresses calculation problem: err = {}, s1 = {}, s2 = {}'.format(err, sPrincipal, sPrincipalSeries[i, :]))
					# Take the ratio of min/max stress
					# V = -1: dominating shear stress
					# V = 0: dominating tension/copression stress
					# V = 1: hydro-static pressure
					if (abs(sPrincipal[0]) > abs(sPrincipal[2])):
						V = sPrincipal[2] / sPrincipal[0]
					else:
						V = sPrincipal[0] / sPrincipal[2]
					# Scale coefficient
					f = 1 + (1 - k) * V
				else:
					f = 1.0
				self.stressesScaled[i, :] = self.stressSeries[i, :] * f

	def computeRotationMatrices(self, numThetaSteps = 10, numPhiSteps = 10):
		self.thetaList = np.arange(numThetaSteps, dtype = np.float64) / numThetaSteps * m.pi
		self.phiList = np.arange(numPhiSteps, dtype = np.float64) / numPhiSteps * m.pi
		self.rotMatrices = np.zeros(shape = (numThetaSteps, numPhiSteps, 3, 3), dtype = np.float64)
		for i in range(numThetaSteps):
			for j in range(numPhiSteps):
				self.rotMatrices[i, j, ...] = STC.getRotationTwoAngleTransf(
					theta = self.thetaList[i], phi = self.phiList[j])
		
	def computeDamage(self):
		#numSamples = self.stressSeries.shape[0]
		#SNCurveParameters = self.SNCurveParameters['Liner']
		#stressValuesFull = np.zeros((numSamples, 3, 3))
		self.damage = np.zeros(shape = (len(self.thetaList), len(self.phiList)), dtype = np.float64)
		for i in range(len(self.thetaList)):
			for j in range(len(self.phiList)):
				rotMatrix = self.rotMatrices[i, j, ...]
				r3 = rotMatrix[2, :]
				# Compute the sigma33 component of the stress tensor in the rotated coordinate system
				sv1 = np.tensordot(self.stressesScaled, r3, axes = ([2], [0]))
				stressValues = np.tensordot(sv1, r3, axes = ([1], [0]))
				if (self.useCompiledExtensions):
					rainflowCalc = Mech.RainflowCounter(self.numStressBins)
					rainflowCalc.setStresses(stressValues)
					rainflowCalc.setMeanStressCorrection(self.meanStressCorrectionFactor)
					rainflowCalc.setSNCurveParameters(self.SNCurveParameters['S_E'], self.SNCurveParameters['N_E'], self.SNCurveParameters['k'])
					self.damage[i, j] = rainflowCalc.compute()
				else:
					from Rainflow import PercentileCalculator, RainflowCounter, DamageCalculator
					# Create bins and distribute stress in bins
					percCalc = PercentileCalculator(stressValues, self.numStressBins)
					# Locate the minima/maxima
					percCalc.locateExtrema()
					# Initialize the rainflow counter
					rainflowCalc = RainflowCounter(percCalc.extremaValues, percCalc.binCenters)
					# Compute the Rainflow mattrix (3-point algorithm)
					rainflowCalc.computeMatrix()
					# Repeat the run on the residual
					rainflowCalc.residualRepeatedRun()
					# Initialize the damage calculator
					damageCalc = DamageCalculator(rainflowCalc.rainflowMatrix, percCalc.binCenters)
					# Set the S-N curve
					#SNCurveParameters = S.SNCurveParameters['Liner']
					#appLogger.info('Calculating with SN curve parameters: k = %f, S_E = %e, N_E = %e' % \
					#			(SNCurveParameters['k'], SNCurveParameters['S_E'], SNCurveParameters['N_E']))
					damageCalc.setSNCurveParameters(
							S_E = self.SNCurveParameters['S_E'], 
							N_E = self.SNCurveParameters['N_E'], 
							k = self.SNCurveParameters['k']
					)
					# Apply mean stress correction to the Rainflow matrix amplitudes 
					damageCalc.applyOneParameterMeanStressCorrection(
							M = self.meanStressCorrectionFactor
					)
					# Compute the cumulative using Palmgren-Miner hypothesis (adding damages)
					self.damage[i, j] = damageCalc.computeDamage()
				
	
	def saveDamage(self, filePath, groupPath = 'Damage/damage'):
		self.dataFile = h5py.File(filePath)
		appLogger.info('Saving damage to %s in file %s'%(groupPath, filePath))
		resGroupPath, datasetName = os.path.split(groupPath)
		if resGroupPath not in self.dataFile:
			self.dataFile.create_group(resGroupPath)
		resGroup = self.dataFile[resGroupPath]
		if (datasetName in resGroup):
			appLogger.warning('Overwriting result stress "%s"'%datasetName)
			del resGroup[datasetName]
		ds = resGroup.create_dataset(datasetName, data = self.damage)
		maxDamage = np.max(self.damage)
		ds.attrs['maxDamage'] = maxDamage		
		appLogger.info('Critical plane damage: %e for "%s"'%(maxDamage, groupPath))
		
def main():
	_logConfigurator = SimpleAppLoggerConfgigurator('MultiaxialDamageCalculator')
	import imp
	try:
		S = imp.load_source('Settings', 'Settings.py')
	except:
		raise RuntimeError('Cannot find settings file "Settings.py"')
	
	# Create stress calculator
	stressCalculator = StressCalculator3D(S.stressTablesPath)
	
	# Create damage calculator
	damageCalculator = MultiaxialDamageCalculator(
				SNCurveParameters=S.SNCurveParameters['Liner'], 
				numStressBins = S.numStressBins, 
				meanStressCorrectionFactor = S.meanStressCorrectionFactor)
	damageCalculator.computeRotationMatrices(numThetaSteps = 36, numPhiSteps = 36)

	# Read each input file
	for fileName in glob.glob(os.path.join(S.experimentSubfolder, '*.csv')):
		dataName, _ = os.path.splitext(os.path.basename(fileName))
		appLogger.info('Reading input file "%s" with (pressure, temperature) data'%fileName)
		data = np.genfromtxt(fileName, delimiter = ',', names = True)
		appLogger.info('Computing stresses')
		# Clean up the data
		data = RecArrayManipulator.removeNaN(data)
		stressCalculator.computeStresses(
					pArr = data['Pressure'],
					TArr = data['Temperature']
		)
		# Write resulting stress
		if (S.writeStressResultsToHdf5):
			stressCalculator.writeStresses(S.stressFile, dataName)
			
		# Calculate damage
		for channel in stressCalculator.channelNames:
			damageCalculator.stressSeries = stressCalculator.stressData[channel]
			damageCalculator.scaleStresses()
			damageCalculator.computeDamage()
			damageCalculator.saveDamage(
				filePath = S.damageFile,
				groupPath = 'Damage' + '/' + dataName + '/' + channel)
	
def stat():
	import pstats, cProfile
	cProfile.runctx('main()', globals(), locals(), "DamageCalc.prof")
	s = pstats.Stats("DamageCalc.prof")
	s.strip_dirs().sort_stats("time").print_stats(20)


# class MultiChannelStressData(object):
# 	def __init__(self, name):
# 		self.name = name
# 
# 	def createArtificialChannels(self, channelGenerators, numSamples):
# 		self.channels = channelGenerators.keys()
# 		self.dtype = [(channel, np.float64, (3, 3)) for channel in self.channels]
# 		self.data = np.zeros(shape = (numSamples,), dtype = self.dtype)
# 		for channel in self.channels:
# 			self.data[channel] = channelGenerators[channel](numSamples)
# 		
# 	
# 	def generatorOscillatingNormalStress(self, amplitude, freq, phase, theta = m.pi/4, phi = m.pi/4):
# 		def generate(n):
# 			Z0 = np.zeros(shape = (n, 3, 3))
# 			Z0[:, 0, 0] = amplitude * np.sin(2 * m.pi * freq * np.arange(n) + phase)
# 			rotMatrix = STC.getRotationTwoAngleTransf(theta = theta, phi = phi)
# 			Z = np.einsum('mi,nj,kij->kmn', rotMatrix, rotMatrix, Z0)
# 			return Z
# 		return generate
# 		
# 	def setRandomData(self, channels, numSamples = 20):
# 		self.channels = channels
# 		self.dtype = [(channel, np.float64, (3, 3)) for channel in self.channels]
# 		self.data = np.zeros(shape = (numSamples,), dtype = self.dtype)
# 		for channel in self.channels:
# 			for i in range(len(self.data[channel])):
# 				x = np.random.rand(3, 3)
# 				self.data[channel][i] = x + x.T
# 			
# 	def getChannel(self, channel):
# 		return self.data[channel]
# 	
# 	@staticmethod
# 	def generateRandomCycles():
# 		stressData = MultiChannelStressData(name = 'RandomCycle')
# 		stressData.setRandomData(['P1', 'P2'], numSamples = 1000)
# 		return stressData
# 	
# 	@staticmethod
# 	def generateOscillatingNormalLoad():
# 		stressData = MultiChannelStressData(name = 'OscillatingNormalLoad')
# 		# Expected result 1.0e-5, actual result 9.46e-6
# 		g1 = stressData.generatorOscillatingNormalStress(1e3, freq = 0.01, phase = 0., theta = m.pi / 4, phi = m.pi / 4)
# 		# Expected result 2.0e-5, actual result 1.9e-5
# 		g2 = stressData.generatorOscillatingNormalStress(1e3, freq = 0.02, phase = 0., theta = m.pi / 4, phi = m.pi / 4)
# 		# Expected result 3.2e-4, actual result 3e-4
# 		g3 = stressData.generatorOscillatingNormalStress(2e3, freq = 0.01, phase = 0., theta = -m.pi / 4, phi = -m.pi / 4)
# 		stressData.createArtificialChannels({'P1': g1, 'P2': g2, 'P3': g3}, numSamples = 10000)
# 		return stressData
