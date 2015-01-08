'''
Created on Jan 8, 2015

@author: Atanas Pavlov
'''

import numpy as np

class Interpolator1D(object):
	"""
	1D interpolator using numpy.interp
	"""
	def __init__(self, xValues, yValues, outOfRange = 'value'):
		self.xValues = np.array(xValues);
		self.yValues = np.array(yValues);
		#self.minX = self.xValues[0]
		#self.maxX = self.xValues[-1]
		

	def __call__(self, inputValues):
		from numpy import interp
		#self.belowMin = inputValues < self.minX
		#self.aboveMax = inputValues > self.maxX
		#limitedValues = inputValues[:]
		#limitedValues[self.belowMin] = self.minX
		#limitedValues[self.aboveMac] = self.maxX
		return interp(inputValues, self.xValues, self.yValues)

class SectionCalculator(object):
	"""
	Perform calculations over a sectioned array object, 
	using different	callable objects for each section	
	"""
	def __init__(self):
		self.sectionIndices = []
		self.calculators = []
	
	def addSection(self, sectionIndices, calculator):
		"""
		:param sectionIndices: a tuple (x1, x2) where x1 is the first 
			index of the section and x2 is the last index
		:param calculator: a callable fn(x) accepting  a single argument
		that will be use used to calculate z = fn(y) over this section 
		"""
		self.sectionIndices.append(sectionIndices)
		self.calculators.append(calculator)
	
	def __call__(self, inputValues):
		results = np.zeros((len(inputValues)))
		for section, calc in zip(self.sectionIndices, self.calculators):
			sectionInputs = inputValues[section[0]:(section[1] + 1)]
			sectionResults = calc(sectionInputs)
			results[section[0]:(section[1] + 1)] = sectionResults
		return results
	
	@classmethod
	def test(cls):
		calc = cls()
		calc.addSection((0, 3), lambda x: 2 * x)
		calc.addSection((5, 9), Interpolator1D(xValues = np.arange(20), yValues = np.arange(20)**2))
		print calc(np.arange(15) + 1)

if __name__ == '__main__':
	SectionCalculator.test()