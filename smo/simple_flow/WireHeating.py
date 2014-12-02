'''
Created on Nov 30, 2014

@author: Atanas Pavlov
'''

import numpy as np
import fipy as fp
from fipy.terms.sourceTerm import SourceTerm

Acs = 2.5e-6
d = np.sqrt(Acs * 4 / np.pi)
print ("d = ", d * 1e3)
As = np.pi * d   
L = 1.

TAmb = 20. # degC
h = 5 # w/m**2-K
eCond = 16.78e-9 # Ohm * m
thermCond = 401.0 # W/m-K

def computeHeatFlux(T):
	return thermCond * Acs / L * (T - TAmb)

class ThermalModel1D:
	def createMesh(self, nx = 5, L = 1.0): 
		""" Define mesh """
		dx = np.ones((nx,)) * float(L) / nx
		self.mesh = fp.Grid1D(dx = dx)
	
	def createEquation(self):
		# Define variable
		self.T = fp.CellVariable(name = "temperature",
			mesh = self.mesh, value = 0.)

		# Define the equation
		c1 = h * dx * As
		print('c1 = ', c1)
		print('q = ', computeHeatFlux(TAmb + 500))
		eqX = fp.DiffusionTerm(coeff = thermCond) + c1 * TAmb - fp.ImplicitSourceTerm(coeff = c1)


		# Boundary conditions
		THigh = 80. # degC
		QGen = 0.5 # W
		self.T.constrain(TAmb, self.mesh.facesLeft)
		#T.constrain(THigh, mesh.facesRight)
		self.T.faceGrad.constrain([QGen / thermCond / Acs], self.mesh.facesRight)
		# Initial conditions
		self.T.setValue(TAmb)
		
		# Run solver
		eqX.solve(var = self.T)
		
		# Plot results
		viewer = fp.Viewer(vars=(self.T,))
		viewer.plot()
		
		# Print results
		#print('qLeft = ', T.grad[])
		print self.T
		print self.T.grad() * Acs * thermCond

model = ThermalModel1D()
model.createMesh()
print model.mesh.dx
