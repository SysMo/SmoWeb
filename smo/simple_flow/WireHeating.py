'''
Created on Nov 30, 2014

@author: Atanas Pavlov
'''

import numpy as np
import fipy as fp
import pylab as plt

class DictObject(object):
	def __init__(self, **kwargs):
		for key, value in kwargs.iteritems():
			self.__dict__[key] = value

Acs = 2.5e-6
d = np.sqrt(Acs * 4 / np.pi)
print ("d = ", d * 1e3)
As = np.pi * d   
L = 1.

TAmb = 20. # degC
h = 5 # w/m**2-K

Copper = DictObject(
	eCond = 16.78e-9, # Ohm * m
	thermalCond = 401.0, # W/m-K
	cp = 385, # J/kg-K
	rho = 8960, # kg/m**3
)

POM = DictObject(
	thermalCond = 0.23, # W/m-K
	cp = 1500, # J/kg-K
	rho = 1420, # kg/m**3
)

#def computeHeatFlux(T):
#	return thermCond * Acs / L * (T - TAmb)

class ThermalModel1D(object):
	def __init__(self):
		self.BCs = (None, None)
		
	def createLinearMesh(self, L, d, n = 50): 
		""" Define mesh """
		self.d = d
		self.areaMult = np.pi / 4 * d * d
		#dx = np.ones((nx,)) * float(L) / nx
		dx = float(L) / n
		self.mesh = fp.Grid1D(nx = n, dx = dx)
		self.meshType = 'Linear'
		# Define variable
		self.T = fp.CellVariable(name = "temperature",
			mesh = self.mesh, value = 0.)
	
	def createRadialMesh(self, rMin, rMax, width, angle = 2 * np.pi, n = 50):
		self.width = width
		self.angle = angle
		self.areaMult = angle * width
		dx = float(rMax - rMin) / n
		self.mesh = fp.CylindricalGrid1D(nx = n, dx = dx, origin = (rMin))
		self.meshType = 'Radial'
		# Define variable
		self.T = fp.CellVariable(name = "temperature",
			mesh = self.mesh, value = 0.)
	
	@property
	def sideFaceAreas(self):
		faceCenters = self.mesh.faceCenters()[0]
		if (self.meshType == 'Linear'):
			faceAreas = np.pi * self.d * (faceCenters[1:] - faceCenters[:-1])
		elif (self.meshType == 'Radial'):
			faceAreas = self.angle / 2 * (faceCenters[1:]**2 - faceCenters[:-1]**2)
		return faceAreas
	
	@property
	def cellVolumes(self):
		pass

	@property
	def heatFluxes(self):
		return - (self.thermalCond * self.T.faceGrad() *  self.mesh.scaledFaceAreas * self.areaMult)

	def setBoundaryConditions(self, side, bcType, value):
		if (side == 0):
			face = self.mesh.facesLeft()
			meshFaceArea = self.mesh.scaledFaceAreas[0]	
		elif (side == 1):
			face = self.mesh.facesRight()
			meshFaceArea = self.mesh.scaledFaceAreas[-1]	
		else:
			raise ValueError('Side must be 0 or 1')

		if (bcType == 'T'):
			self.T.constrain(value, face)
		elif (bcType == 'Q'):
			faceArea = meshFaceArea * self.areaMult
			gradValue = value / faceArea / self.thermalCond
			self.T.faceGrad.constrain([-gradValue], face)
		else:
			raise ValueError('BC type must be T(temperature) or Q(heat flux)')
		
	def solve(self):
		sideFaceFactor = fp.CellVariable(name = "sideFaceFactor",
			mesh = self.mesh, value = self.sideFaceAreas / (self.areaMult * self.mesh.cellVolumes))
						
		eqX = fp.DiffusionTerm(coeff = self.thermalCond) +  self.h * (sideFaceFactor * TAmb - fp.ImplicitSourceTerm(coeff = sideFaceFactor))
		# Initial conditions
		self.T.setValue(TAmb)
		# Run solver
		eqX.solve(var = self.T)				
	
	def plotTemperature(self):
		# Print results
		cellCenters = self.mesh.cellCenters.value[0]
		plt.plot(cellCenters, self.T, 'b')
		plt.show()

model = ThermalModel1D()
model.thermalCond = Copper.thermalCond
model.createLinearMesh(L = 1, d = 1.784e-3, n = 30)
#model.thermalCond = POM.thermalCond
#model.createRadialMesh(rMin = 0.005, rMax = 0.2, width = 3.0e-3, n = 50)
model.setBoundaryConditions(0, 'T', 80)
model.setBoundaryConditions(1, 'T', 20)
model.h = 5
model.solve()
print model.heatFluxes[0][0]
model.plotTemperature()