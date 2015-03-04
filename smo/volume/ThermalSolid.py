'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

import numpy as np
from smo.math.util import Interpolator1D
from smo.media.MaterialData import Solids
from Structures import HeatFlow, ThermalState, ThermalPort

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
		
		if (self.numConductiveSegments > 0):
			self.segmentThickness =  self.thickness / self.numConductiveSegments
			self.conductionArea = conductionArea
			self.cond = np.zeros(self.numConductiveSegments)
			self.QDot = np.zeros(self.numConductiveSegments)
		
		# Set up the port valriables
		self.port1 = ThermalPort()
		self.port2 = ThermalPort()
	
	def setState(self, TVect):
		self.T = TVect[:]
		if (self.side1Type == 'C'):
			self.port1.state.T = self.T[0]
		if (self.side2Type == 'C'):
			self.port2.state.T = self.T[-1]

	def compute(self):
		# Read port variables
		if (self.side1Type == 'R'):
			self.T1Ext = self.port1.state.T
		else:
			self.Q1DotExt = self.port1.flow.qDot
		if (self.side2Type == 'R'):
			self.T2Ext = self.port2.state.T
		else:
			self.Q2DotExt = self.port2.flow.qDot
		
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
			self.TDot[0] += self.Q1DotExt / (self.segmentMass * self.cp[0])
			a = 0

		if (self.side2Type == 'R'):
			self.cond[-1] = self.thermCondModel((self.T[-1] + self.port2.state.T)/2)
			self.QDot[-1] = self.cond[-1] * self.conductionArea / self.segmentThickness * (self.T[-1] -  self.port2.state.T)
			self.TDot[-1] -= self.QDot[-1] / (self.segmentMass * self.cp[-1])
			b = 1
		else:
			self.TDot[-1] += self.Q2DotExt / (self.segmentMass * self.cp[-1])
			b = 0
			
		for i in range(a, self.numConductiveSegments - b):
			self.cond[i] = self.thermCondModel((self.T[i - a] + self.T[i + 1 - a])/2)
			self.QDot[i] = self.cond[i] * self.conductionArea / self.segmentThickness * (self.T[i - a] -  self.T[i + 1 - a])
			self.TDot[i - a] -= self.QDot[i] / (self.segmentMass * self.cp[i - a])
			self.TDot[i + 1 - a] += self.QDot[i] / (self.segmentMass * self.cp[i + 1 - a])
			
		# Write port variables
		if (self.side1Type == 'R'):
			self.Q1DotExt = self.QDot[0]
		else:			
			pass # Already done in setState 
		if (self.side2Type == 'R'):
			self.Q2DotExt = self.QDot[-1]
		else:			
			pass # Already done in setState 


def testSolidConductiveBody():
	print "=== START: Test SolidConductiveBody ==="
	
	# Initial the conduction body
	import pylab as plt
	numbMassSegments = 4
	
	# Tank (Liner)
	scBody_Liner = SolidConductiveBody(
			material = 'Aluminium6061', 
			mass = 24., #[kg]
			thickness = 0.004, #[m]
			conductionArea = 1.8, #[m**2]
			side1Type = 'R', side2Type = 'C', 
			numMassSegments = 1, 
			TInit = 300 #[K]
			)
	
	# Tank (composite)
	scBody = SolidConductiveBody(
			material = 'CarbonFiberComposite', 
			mass = 34., #[kg]
			thickness = 0.0105, #[m]
			conductionArea = 1.8, #[m**2]
			side1Type = 'R', side2Type = 'C', 
			numMassSegments = numbMassSegments, 
			TInit = 300 #[K]
			)
	
	# Simulation parameters
	scBody.port1.state.T = 300 #[K]
	scBody.port2.flow.qDot = 5e3 #[W]
	
	t = 0.0
	dt = 1.
	tFinal = 1000
	
	tPrintInterval = dt*10
	tFinal += tPrintInterval
	tNextPrint = 0
	iPrint = 0
	numIterStep = int(tFinal/dt)
	
	# Run Simulation
	TSegments = np.zeros((int(tFinal/tPrintInterval), numbMassSegments + 1))
	for i in range(numIterStep):
		scBody.compute()
		scBody.setState(scBody.T + scBody.TDot * dt)
		
		# Print results
		if t >= tNextPrint:
			TSegments[iPrint, :] = np.append(t, scBody.T[:])
			tNextPrint = t + tPrintInterval - dt/10
			iPrint += 1
		t += dt
	
	# Write the result to csv file
	np.savetxt("./test/SolidConductiveBody_Results.csv", TSegments, delimiter=",")
	
	# Plot the result
	plt.plot(TSegments[:,0], TSegments[:,1:])
	plt.show()
	
	print "=== END: Test SolidConductiveBody ==="
	
	
if __name__ == '__main__':
	testSolidConductiveBody()