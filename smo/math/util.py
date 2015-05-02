'''
Created on Jan 8, 2015

@author: Atanas Pavlov
'''

import numpy as np
import math

def formatNumber(n, sig = 6):
	'''
	Converts a floating point number to a string using
	the given number of significant digits.
	:param sig: number of significant digits
	'''
	if (n == 0):
		return '0'		
	if (abs(n) < 1e-80):
		return '0'
	if (abs(n) > 1e5 or abs(n) < 1e-3):
		return '{:.3e}'.format(n)
	mult = math.pow(10, sig - math.floor(math.log10(abs(n))) - 1)
	return str(round(n * mult) / mult)

def cart2pol(x, y):
	'''
	Converts Cartesian coordinates (x,y) to Polar coordinates (rho, phi)
	'''
	rho = np.sqrt(x**2 + y**2)
	phi = np.arctan2(y, x)
	return (rho, phi)

def pol2cart(rho, phi):
	'''
	Converts Polar coordinates (rho, phi) to Cartesian coordinates (x,y)
	'''
	x = rho * np.cos(phi)
	y = rho * np.sin(phi)
	return (x, y)

class Interpolator1D(object):
	"""
	1D interpolator using numpy.interp. Allows the values to be
	set only once in the constructor, and then called as a function.
	"""
	def __init__(self, xValues, yValues, outOfRange = 'value'):
		self.xValues = np.array(xValues);
		self.yValues = np.array(yValues);		

	def __call__(self, inputValues):
		from numpy import interp
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
	"""
	A data structure which has two different views. 
	On one hand it is a vector of values (of the same type),
	on the other hand each value can be accessed by name, as though
	it is a member variable of the class.
	"""
	def __init__(self, stateList):
		from collections import OrderedDict
		self.__dict__['stateMap'] = OrderedDict((zip(stateList, range(len(stateList)))))
		self.__dict__['_values'] = np.zeros((len(stateList)))

	def set(self, values, copy = False):
		'''
		Sets variable values from a numpy vector
		'''
		if (copy):
			self.__dict__['_values'] = values[:]
		else:  
			self.__dict__['_values'] = values
	
	def get(self, copy = False):
		'''
		Sets numpy array's values from the internal storage
		'''
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

class RecArrayManipulator(object):
	@staticmethod
	def removeNaN(a):
		cols = a.dtype.fields.keys()
		nanRows = np.zeros(shape = (a.shape[0],), dtype = np.bool)
		for col in cols:
			testNaN = np.isnan(a[col])
			nanRows |= testNaN
		numRowToRemove = len(a[nanRows])
#		appLogger.info('%d rows with NaNs removed from %d rows total'%(numRowToRemove, len(a)))
		newLen = len(a) - numRowToRemove
		newArray = np.empty((newLen,), dtype=a.dtype)
		for col in cols:
			newArray[col] = a[col][~nanRows]
		return newArray
	
if __name__ == '__main__':
	SectionCalculator.test()
	NamedStateVector.test()
