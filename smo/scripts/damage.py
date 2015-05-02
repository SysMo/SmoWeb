import glob, os
import numpy as np
from smo.math.util import RecArrayManipulator
from smo.util.log import SimpleAppLoggerConfgigurator
from smo.mechanical.StressCalculator3D import StressCalculator3D
from smo.mechanical.MultiaxialDamangeCalculator import MultiaxialDamageCalculator

import logging
appLogger = logging.getLogger('AppLogger')

def main():
	_logConfigurator = SimpleAppLoggerConfgigurator('MultiaxialDamageCalculator')
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
	
if __name__ == '__main__':
	import imp
	try:
		S = imp.load_source('Settings', 'Settings.py')
	except:
		raise RuntimeError('Cannot find settings file "Settings.py"')
	main()
	#stat()
