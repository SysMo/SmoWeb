'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.math.util import Interpolator1D
from smo.media.MaterialData import Solids
import numpy as np

class SolidConductiveBody(object):
	def __init__(self, material, mass, thickness = None, conductionArea = None, 
				side1Type = 'C', side2Type = 'C', numMassSegments = 1, TInit = 288.15):
		
		# Set the material
		if (isinstance(material, basestring)):
			self.material = Solids[material]
		elif (isinstance(material, dict)):
			self.material = material
		# Thermal conductivity model
		if ('thermalCond_T' in self.material):
			self.thermCondModel = Interpolator1D(
					xValues = self.material['thermalCond_T']['T'],
					yValues = self.material['thermalCond_T']['cond'])
		else:
			raise ValueError("The material '{}' does not define a thermal conductivity model".format(self.material.name))
		# Heat capacity model
		if ('heatCapacity_T' in self.material):
			self.cpModel = Interpolator1D(
					xValues = self.material['heatCapacity_T']['T'],
					yValues = self.material['heatCapacity_T']['cp'])
		else:
			raise ValueError("The material '{}' does not define a thermal conductivity model".format(self.material.name))
		# Mass
		self.mass = mass
		self.numMassSegments = numMassSegments
		self.segmentMass= mass / numMassSegments
		self.cp = np.zeros(self.numMassSegments)
		self.T = np.ones(self.numMassSegments) * TInit
		self.TDot = np.zeros(self.numMassSegments)
		
		# Conductions and end handling
		self.thickness = thickness
		self.numConductiveSegments = self.numMassSegments - 1
		if (side1Type in ['C', 'R']):
			self.side1Type = side1Type
			if (side1Type == 'R'):
				self.numConductiveSegments += 1
		else:
			raise ValueError("side1Type must be 'R' or 'C', value given is '{}'".format(side1Type))
		if (side2Type in ['C', 'R']):
			self.side2Type = side2Type
			if (side2Type == 'R'):
				self.numConductiveSegments += 1
		else:
			raise ValueError("side2Type must be 'R' or 'C', value given is '{}'".format(side2Type))
		
		self.segmentThickness =  self.thickness / self.numConductiveSegments
		self.conductionArea = conductionArea
		self.cond = np.zeros(self.numConductiveSegments)
		self.QDot = np.zeros(self.numConductiveSegments)
		
	def compute(self):
		self.TDot *= 0.0
		# Compute heat capacities
		for i in range(self.numMassSegments):
			self.cp[i] = self.cpModel(self.T[i])
		# Compute conductivities, heat flow rates and temperature derivatives
		if (self.side1Type == 'R'):
			self.cond[0] = self.thermCondModel((self.T1Ext +  self.T[0])/2)
			self.QDot[0] = self.cond[0] * self.conductionArea / self.segmentThickness * (self.T1Ext -  self.T[0])
			self.TDot[0] += self.QDot[0] / (self.segmentMass * self.cp[0])
			a = 1
		else:
			self.TDot[0] += self.QDot1Ext / (self.segmentMass * self.cp[0])
			a = 0

		if (self.side2Type == 'R'):
			self.cond[-1] = self.thermCondModel((self.T[-1] - self.T2Ext)/2)
			self.QDot[-1] = self.cond[-1] * self.conductionArea / self.segmentThickness * (self.T[-1] -  self.T2Ext)
			self.TDot[-1] += self.QDot[-1] / (self.segmentMass * self.cp[-1])
			b = 1
		else:
			self.TDot[-1] += self.QDot2Ext / (self.segmentMass * self.cp[-1])
			b = 0
			
		for i in range(a, self.numConductiveSegments - b):
			self.cond[i] = self.thermCondModel((self.T[i - a] + self.T[i + 1 - a])/2)
			self.QDot[i] = self.cond[i] * self.conductionArea / self.segmentThickness * (self.T[i - a] -  self.T[i + 1 - a])
			self.TDot[i - a] -= self.QDot[i] / (self.segmentMass * self.cp[i - a])
			self.TDot[i + 1 - a] += self.QDot[i] / (self.segmentMass * self.cp[i + 1 - a])

def main():
	import pylab as plt
	sm = SolidConductiveBody(material = 'Aluminium6061', mass = 40., thickness = 1.0, 
			conductionArea = 1e-4, side1Type = 'C', side2Type = 'R', numMassSegments = 5)
	sm.QDot1Ext = 10
	sm.T2Ext = 288.15
	dt = 1.0
	T1 = np.zeros((100000, 2))
	for i in range(100000):
		sm.compute()
		sm.T += sm.TDot * dt
		T1[i, 0] = sm.T[0]
		T1[i, 1] = sm.T[1]
	plt.plot(T1)
	plt.show()
if __name__ == '__main__':
	main()