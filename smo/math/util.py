'''
Created on Jan 8, 2015

@author: Atanas Pavlov
'''

import numpy as np
import math

def formatNumber(n, sig = 6):
	if (n == 0):
		return '0'		
	if (abs(n) < 1e-80):
		return '0'
	if (abs(n) > 1e5 or abs(n) < 1e-3):
		return '{:.3e}'.format(n)
	mult = math.pow(10, sig - math.floor(math.log10(abs(n))) - 1)
	return str(round(n * mult) / mult)

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

class NamedStateVector(object):
	def __init__(self, stateList):
		from collections import OrderedDict
		self.__dict__['stateMap'] = OrderedDict((zip(stateList, range(len(stateList)))))
		self.__dict__['_values'] = np.zeros((len(stateList)))

	def set(self, values, copy = False):
		if (copy):
			self.__dict__['_values'] = values[:]
		else:  
			self.__dict__['_values'] = values
	
	def get(self, copy = False):
		if (copy):
			values = self._values[:]
		else:  
			values = self._values
		return values
	
	def getColIndex(self, colName):
		colIndex = self.stateMap.get(colName, None)
		return colIndex
	
	def __setattr__(self, attr, value):
		self._values[self.stateMap[attr]] = value

	def __getattr__(self, attr):
		return self._values[self.stateMap[attr]]
		
	@staticmethod
	def test():
		a = NamedStateVector(['T', 'p', 'h'])
		n1 = np.array([3, 7, 4], copy = True)
		a.set(n1)
		print('T = {}, p = {}, h = {}'.format(a.T, a.p, a.h))
		a.T = 56
		a.h = -20
		print('T = {}, p = {}, h = {}'.format(a.T, a.p, a.h))
		print (a.get())

if __name__ == '__main__':
	SectionCalculator.test()
	NamedStateVector.test()
