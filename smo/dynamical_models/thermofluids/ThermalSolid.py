'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.dynamical_models.core as DMC
from smo.dynamical_models.thermofluids import Structures as DMS
from smo.media.MaterialData import Solids
from smo.math.util import Interpolator1D
from smo.util import AttributeDict

class SolidConductiveBody(DMC.DynamicalModel):
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		# Set the material
		if (isinstance(params.material, basestring)):
			self.material = Solids[params.material]
		elif (isinstance(params.material, dict)):
			self.material = params.material
	
		# Thermal conductivity params
		if ('thermalCond_T' in self.material):
			self.thermCondModel = Interpolator1D(
					xValues = self.material['thermalCond_T']['T'],
					yValues = self.material['thermalCond_T']['cond'])
		else:
			raise ValueError("The material '{}' does not define a thermal conductivity params".format(self.material.name))
		# Heat capacity params
		if ('heatCapacity_T' in self.material):
			self.cpModel = Interpolator1D(
					xValues = self.material['heatCapacity_T']['T'],
					yValues = self.material['heatCapacity_T']['cp'])
		else:
			raise ValueError("The material '{}' does not define a thermal conductivity params".format(self.material.name))
		
		# Mass
		if hasattr(params, 'mass'):
			self.mass = params.mass
		else:
			rho = self.material['refValues']['density']
			V = params.thickness * params.conductionArea
			self.mass = rho * V
		
		self.numMassSegments = params.numMassSegments
		self.segmentMass= self.mass / self.numMassSegments
		self.cp = np.zeros(self.numMassSegments)
		self.T = np.ones(self.numMassSegments) * params.TInit
		self.TDot = np.zeros(self.numMassSegments)
		
		# Conductions and end handling
		self.thickness = params.thickness
		self.numConductiveSegments = self.numMassSegments - 1
		if (params.port1Type in ['C', 'R']):
			if (params.port1Type == 'R'):
				self.numConductiveSegments += 1
		else:
			raise ValueError("port1Type must be 'R' or 'C', value given is '{}'".format(params.port1Type))
		if (params.port2Type in ['C', 'R']):
			if (params.port2Type == 'R'):
				self.numConductiveSegments += 1
		else:
			raise ValueError("port2Type must be 'R' or 'C', value given is '{}'".format(params.port2Type))
		
		if (self.numConductiveSegments > 0):
			self.segmentThickness =  self.thickness / self.numConductiveSegments
			self.conductionArea = params.conductionArea
			self.cond = np.zeros(self.numConductiveSegments)
			self.QDot = np.zeros(self.numConductiveSegments)
		
		# Set up the port valriables
		if (params.port1Type == 'C'):
			self.port1 = DMS.ThermalPort(params.port1Type, DMS.ThermalState())
		else:
			self.port1 = DMS.ThermalPort(params.port1Type)
			
		if (params.port2Type == 'C'):
			self.port2 = DMS.ThermalPort(params.port2Type, DMS.ThermalState())
		else:
			self.port2 = DMS.ThermalPort(params.port2Type)
	
	def setState(self, T):
		self.T[:] = T
		if (self.port1.portType == 'C'):
			self.port1.state.T = self.T[0]
		if (self.port2.portType == 'C'):
			self.port2.state.T = self.T[-1]

	def compute(self):
		# Read port variables
		if (self.port1.portType == 'R'):
			self.T1Ext = self.port1.state.T
		else:
			self.Q1DotExt = self.port1.flow.QDot
			
		if (self.port2.portType == 'R'):
			self.T2Ext = self.port2.state.T
		else:
			self.Q2DotExt = self.port2.flow.QDot
		
		self.TDot *= 0.0
		# Compute heat capacities
		for i in range(self.numMassSegments):
			self.cp[i] = self.cpModel(self.T[i])
		# Compute conductivities, heat flow rates and temperature derivatives
		if (self.port1.portType == 'R'):
			self.cond[0] = self.thermCondModel((self.T1Ext +  self.T[0])/2)
			self.QDot[0] = self.cond[0] * self.conductionArea / self.segmentThickness * (self.T1Ext -  self.T[0])
			self.TDot[0] += self.QDot[0] / (self.segmentMass * self.cp[0])
			a = 1
		else:
			self.TDot[0] += self.Q1DotExt / (self.segmentMass * self.cp[0])
			a = 0

		if (self.port2.portType == 'R'):
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
		if (self.port1.portType == 'R'):
			self.Q1DotExt = -self.QDot[0]
			self.port1.flow.QDot = self.Q1DotExt
		else:			
			pass # Already done in setState 
		
		if (self.port2.portType == 'R'):
			self.Q2DotExt = self.QDot[-1]
			self.port2.flow.QDot = self.Q2DotExt
		else:			
			pass # Already done in setState 


def testSolidConductiveBody():
	print "=== START: Test SolidConductiveBody ==="
	
	# Initial the conduction body
	import pylab as plt
	numbMassSegments = 4
	
	# Tank (composite)
	scBody = SolidConductiveBody(
		material = 'CarbonFiberComposite', 
		mass = 100., #[kg]
		thickness = 0.01, #[m]
		conductionArea = 10, #[m**2]
		port1Type = 'R', port2Type = 'C', 
		numMassSegments = numbMassSegments, 
		TInit = 300 #[K]
	)
	
	# Simulation parameters
	T1 = 300 #[K]
	qDot2 = 5e3 #[W]
	extPort1 = DMS.ThermalPort('C', DMS.ThermalState(T = T1))
	extPort2 = DMS.ThermalPort('R', DMS.HeatFlow(qDot = qDot2))
	scBody.port1.connect(extPort1) 
	scBody.port2.connect(extPort2)
	
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
	for _i in range(numIterStep):
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