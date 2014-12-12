'''
Created on Nov 30, 2014

@author: Atanas Pavlov
'''

import numpy as np
import fipy as fp
import pylab as plt
from smo.numerical_model.model import NumericalModel
from smo.numerical_model.fields import *
from collections import OrderedDict
from fipy.variables.faceVariable import FaceVariable

class DictObject(object):
	def __init__(self, **kwargs):
		for key, value in kwargs.iteritems():
			self.__dict__[key] = value

# Acs = 2.5e-6
# d = np.sqrt(Acs * 4 / np.pi)
# print ("d = ", d * 1e3)
# As = np.pi * d   
# L = 1.
# 
# TAmb = 20. # degC
# h = 5 # w/m**2-K
# 
# Copper = DictObject(
# 	eCond = 16.78e-9, # Ohm * m
# 	thermalCond = 401.0, # W/m-K
# 	cp = 385, # J/kg-K
# 	rho = 8960, # kg/m**3
# )
# 
# POM = DictObject(
# 	thermalCond = 0.23, # W/m-K
# 	cp = 1500, # J/kg-K
# 	rho = 1420, # kg/m**3
# )

#def computeHeatFlux(T):
#	return thermCond * Acs / L * (T - TAmb)

sigmaSB = 5.67e-8

class ThermalModel1D(object):
	def __init__(self, TAmb):
		self.BCs = (None, None)
		self.TAmb = TAmb
		self.radiation = {
			'active' : False,
			'epsilon' : 1
		}
		self.solver = {
			'nonlinear': False,
			'tolerance': 1e-8,
			'maxIterations': 1000
		}
		
	def createLinearMesh(self, L, Acs, As, n = 50): 
		""" Define mesh """
		# Cross sectional area
		self.Acs = Acs
		# Area multiplier for face area
		self.areaMult = Acs
		# Surface area per unit length
		self.As = As
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
			faceAreas = self.As * (faceCenters[1:] - faceCenters[:-1])
		elif (self.meshType == 'Radial'):
			faceAreas = self.angle / 2 * (faceCenters[1:]**2 - faceCenters[:-1]**2)
		return faceAreas
	
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
						
		eqX = fp.DiffusionTerm(coeff = self.thermalCond)
		if (self.radiation['active']):
			epsilon = self.radiation['epsilon']
			eqX = eqX + sigmaSB * epsilon * (sideFaceFactor * self.TAmb**4 - fp.ImplicitSourceTerm(coeff = sideFaceFactor * self.T**3))
		#+  self.h * (sideFaceFactor * TAmb - fp.ImplicitSourceTerm(coeff = sideFaceFactor))
		# Initial conditions
		self.T.setValue(self.TAmb)
		# Run solver
		if (self.solver['nonlinear']):
			res = 1
			sweep = 0
			self.resVector = [res]
			while (res > self.solver['tolerance'] and sweep < self.solver['maxIterations']):
				res = eqX.sweep(self.T, underRelaxation = 1.0)
				sweep += 1
				self.resVector.append(res)							
		else:
			eqX.solve(var = self.T)
		
		self.Q = FaceVariable(mesh = self.mesh, value = - self.thermalCond * self.areaMult * self.mesh.scaledFaceAreas * self.T.faceGrad)
	
	def plotTemperature(self):
		# Print results
		cellCenters = self.mesh.cellCenters.value[0]
		plt.plot(cellCenters, self.T, 'b')
		plt.show()

BoundaryConditionChoice = OrderedDict((
	('T', 'temperature'),
	('Q', 'heat flux')	
	))

class WireHeating1D(NumericalModel):
	d = Quantity('Length', default = (2, 'mm'), label = 'diameter')
	L = Quantity('Length', default = (1, 'm'), label = 'length')
	n = Quantity('Dimensionless', default = 50, maxValue=200, label = 'num. elements')
	thermalCond = Quantity('ThermalConductivity', default = 401, label = 'thermal conductivity')
	eCond = Quantity('ElectricalConductivity', default = 5.96e7, label = 'electrical conductivity')
	I = Quantity('ElectricalCurrent', default = (10, 'A'), label = 'electrical current')
	g1 = FieldGroup([d, L, n, thermalCond, eCond, I], label = 'Wire')
	
	bcLeft = Choices(BoundaryConditionChoice, label='boundary condition (left)')
	TLeftInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeftInput = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	bcRight = Choices(BoundaryConditionChoice, label='boundary condition (right)')
	TRightInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRightInput = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	h = Quantity('HeatTransferCoefficient', default = (10, 'W/m**2-K'), label = 'convection coefficient')	
	g2 = FieldGroup([bcLeft, TLeftInput, QLeftInput, bcRight, TRightInput, QRightInput, h], label = 'Boundary conditions')
	
	inputs = SuperGroup([g1, g2]) 
	#####################
	Acs = Quantity('Area', default = (1, 'mm**2'), label = 'cross sectional area')
	As = Quantity('Area', default = (1, 'mm**2'), label = 'surface area')
	r1 = FieldGroup([Acs, As], label = 'Res') 
	
	TLeft = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeft = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	TRight = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRight = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	
	results = SuperGroup([r1])
	
	def compute(self):
		self.Acs = np.pi/4 * self.d * self.d
		self.As = np.pi * self.d * self.L
		
		# Create the thermal model object
		model = ThermalModel1D()
		# Create mesh
		model.createLinearMesh(L = self.L, d = self.d, n = self.n)
		# Set boundary conditions
		if (self.bcLeft == 'T'):
			model.setBoundaryConditions(0, 'T', self.TLeftInput)
		else:
			model.setBoundaryConditions(0, 'Q', self.QLeftInput)
		
		if (self.bcRight == 'T'):
			model.setBoundaryConditions(1, 'T', self.TRightInput)
		else:
			model.setBoundaryConditions(1, 'Q', self.QRightInput)
			
# model = ThermalModel1D()
# model.thermalCond = Copper.thermalCond
# model.createLinearMesh(L = 1, d = 1.784e-3, n = 30)
# #model.thermalCond = POM.thermalCond
# #model.createRadialMesh(rMin = 0.005, rMax = 0.2, width = 3.0e-3, n = 50)
# model.setBoundaryConditions(0, 'T', 80)
# model.setBoundaryConditions(1, 'T', 20)
# model.h = 5
# model.solve()
# print model.heatFluxes[0][0]
# model.plotTemperature()

class CryogenicPipe(NumericalModel):
	d_int = Quantity('Length', default = (5, 'mm'), label = 'internal diameter')
	d_ext = Quantity('Length', default = (10, 'mm'), label = 'external diameter')
	L = Quantity('Length', default = (1, 'm'), label = 'length')
	n = Quantity(default = 50, maxValue=200, label = 'num. elements')
	thermalCond = Quantity('ThermalConductivity', default = 401, label = 'thermal conductivity')
	computeRadiation = Boolean(default = True, label = 'compute radiation')
	emissivity = Quantity(default = 0.5, maxValue=1.0, label = 'emissivity', show = 'self.computeRadiation')
	g1 = FieldGroup([d_int, d_ext, L, n, thermalCond, computeRadiation, emissivity], label = 'Pipe')
	
	bcLeft = Choices(BoundaryConditionChoice, label='boundary condition (left)')
	TLeftInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeftInput = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	bcRight = Choices(BoundaryConditionChoice, label='boundary condition (right)')
	TRightInput = Quantity('Temperature', default = (40, 'K'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRightInput = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	TAmb = Quantity('Temperature', default = (20, 'degC'), label = 'ambient temperature')
	g2 = FieldGroup([bcLeft, TLeftInput, QLeftInput, bcRight, TRightInput, QRightInput, TAmb], label = 'Boundary conditions')
	
	inputs = SuperGroup([g1, g2]) 
	
	#####################
	
	Acs = Quantity('Area', default = (1, 'mm**2'), label = 'conduction area')
	As = Quantity('Area', default = (1, 'mm**2'), label = 'surface area')
	r1 = FieldGroup([Acs, As], label = 'Res') 
	r1g = SuperGroup([r1], label = 'Values')

	T_x = PlotView(options = {'title': 'Temperature', 'labels': ['x position [m]', 'temperature [K]']})
	Q_x = PlotView(options = {'title': 'Axial heat flow', 'labels': ['x position [m]', 'heat flow [W]']})
	r2 = ViewGroup([T_x], label =  'Distributions')
	r2g = SuperGroup([r2], label = 'Distributions')
	
	residual = PlotView(options = {'title': 'Residual', 'labels': ['iteration #', 'residual']})
	r3 = ViewGroup([residual], label = 'Convergence')
	r3g = SuperGroup([r3], label = 'Convergence')
	
	results = [r1g, r2g, r3g]
	
	def compute(self):
		self.Acs = np.pi/4 * (self.d_ext * self.d_ext - self.d_int * self.d_int)
		self.As = np.pi * self.d_ext * self.L
		
		# Create the thermal model object
		model = ThermalModel1D(self.TAmb)
		model.thermalCond = self.thermalCond
		# Create mesh
		model.createLinearMesh(L = self.L, Acs = self.Acs, As = self.As, n = self.n)
		# Set boundary conditions
		if (self.bcLeft == 'T'):
			model.setBoundaryConditions(0, 'T', self.TLeftInput)
		else:
			model.setBoundaryConditions(0, 'Q', self.QLeftInput)
		
		if (self.bcRight == 'T'):
			model.setBoundaryConditions(1, 'T', self.TRightInput)
		else:
			model.setBoundaryConditions(1, 'Q', self.QRightInput)
		# Activate radiation if necessary
		if (self.computeRadiation):
			model.radiation['active'] = True
			model.radiation['epsilon'] = self.emissivity
		
		model.solver['nonlinear'] = True
		model.solver['tolerance'] = 1e-7
		model.solver['maxIterations'] = 1000
		model.solve()
		
		resArray = np.zeros((self.n, 2))
		resArray[:, 0] = model.mesh.cellCenters.value[0]
		resArray[:, 1] = model.T
		self.T_x = ViewContent(data = resArray, columnLabels = ['x position [m]', 'temperature [K]'])
		
		Qx = np.zeros((self.n, 2))
		Qx[:, 0] = model.mesh.cellCenters.value[0]
		Qx[:, 1] = model.Q
		self.Q_x = ViewContent(data = Qx, columnLabels = [])
		
		
		numIter = len(model.resVector)
		residual = np.zeros((numIter, 2))
		residual[:, 0] = np.arange(numIter)
		residual[:, 1] = model.resVector
		self.residual = ViewContent(data = residual, columnLabels = ['iteration #', 'residual'])

		

			