'''
Created on Nov 30, 2014

@author: Atanas Pavlov
'''

import numpy as np
#import pylab as plt
from smo.numerical_model.model import NumericalModel
from smo.numerical_model.fields import *
from collections import OrderedDict
import fipy as fp
from fipy.solvers.pysparse import LinearLUSolver
#from fipy.boundaryConditions.fixedFlux import FixedFlux

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
from scipy.interpolate import interp1d
StainlessSteel = {
	'thermalCond_T': {
		'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0, 400.0],
		'cond': [1.95, 5.8, 7.94, 9.4, 10.6, 11.5, 12.3, 13, 13.6, 14.1, 14.5, 14.9, 14.9],
	},
	'emissivity_T':{
		'T': [0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 200.0, 300.0, 400],
		'epsilon': [0, 0.036, 0.039, 0.044, 0.048, 0.051, 0.055, 0.058, 0.062, 0.064, 0.0985, 0.1385, 0.1385]
	}
}

sigmaSB = 5.67e-8

class ThermalModel1D(object):
	def __init__(self, TAmb):
		self.BCs = (None, None)
		self.TAmb = TAmb
		self.radiation = {
			'active' : False,
		}
		self.solverSettings = {
			'nonlinear': False,
			'tolerance': 1e-8,
			'maxIterations': 1000,
			'relaxationFactor': 1.0
		}
		self.thermCondModel = interp1d(StainlessSteel['thermalCond_T']['T'], StainlessSteel['thermalCond_T']['cond'])
		self.emissivityModel = interp1d(StainlessSteel['emissivity_T']['T'], StainlessSteel['emissivity_T']['epsilon'])
		
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
		self.thermCond = fp.FaceVariable(mesh = self.mesh)
		self.emissivity = fp.CellVariable(mesh = self.mesh)
	
# 	def createRadialMesh(self, rMin, rMax, width, angle = 2 * np.pi, n = 50):
# 		self.width = width
# 		self.angle = angle
# 		self.areaMult = angle * width
# 		dx = float(rMax - rMin) / n
# 		self.mesh = fp.CylindricalGrid1D(nx = n, dx = dx, origin = (rMin))
# 		self.meshType = 'Radial'
# 		# Define variable
# 		self.T = fp.CellVariable(name = "temperature",
# 			mesh = self.mesh, value = 0.)
	
	@property
	def sideFaceAreas(self):
		faceCenters = self.mesh.faceCenters()[0]
		if (self.meshType == 'Linear'):
			faceAreas = self.As * (faceCenters[1:] - faceCenters[:-1])
		elif (self.meshType == 'Radial'):
			faceAreas = self.angle / 2 * (faceCenters[1:]**2 - faceCenters[:-1]**2)
		return faceAreas
	
	@property
	def QAx(self):
		return fp.FaceVariable(mesh = self.mesh, value = - self.thermCond * self.areaMult * self.mesh.scaledFaceAreas * self.T.faceGrad)	
	@property
	def QRad(self):
		return fp.CellVariable(mesh = self.mesh, value = sigmaSB * self.emissivity * (self.As * (self.TAmb**4 - self.T**4)))
	@property
	def minT(self):
		return np.min(self.T())
	@property
	def maxT(self):
		return np.max(self.T())


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
			raise NotImplementedError('Heat boundary condition not yet implemented')
			faceArea = meshFaceArea * self.areaMult
			gradValue = value / faceArea / self.thermalCond
			self.T.faceGrad.constrain([-gradValue], face)
		else:
			raise ValueError('BC type must be T(temperature) or Q(heat flux)')
		
	def solve(self):
		sideFaceFactor = fp.CellVariable(name = "sideFaceFactor",
			mesh = self.mesh, value = self.sideFaceAreas / (self.areaMult * self.mesh.cellVolumes))

		#+  self.h * (sideFaceFactor * TAmb - fp.ImplicitSourceTerm(coeff = sideFaceFactor))
		# Initial conditions
		self.T.setValue(self.TAmb)
		# Run solverSettings
		solver = LinearLUSolver(tolerance=1e-10)
		if (self.solverSettings['nonlinear']):
			res = 1
			sweep = 0
			self.resVector = [res]
			TFaces = self.T.arithmeticFaceValue()
			self.TLeft = [TFaces[0]]
			self.TRight = [TFaces[-1]]
			self.QLeft = [self.QAx[0]]
			self.QRight = [self.QAx[-1]]
			while (res > self.solverSettings['tolerance'] and sweep < self.solverSettings['maxIterations']):
				# Compute temperature dependent thermal conductivity 
				self.thermCond.setValue(self.thermCondModel(TFaces))
				# Add the conductivity term to the equation					
				eqX = fp.DiffusionTerm(coeff = self.thermCond)
				if (self.radiation['active']):
					# Compute temperature dependent emissivity
					self.emissivity.setValue(self.emissivityModel(self.T))
					# Add radiation term to the equation
					radMultiplier = sigmaSB * self.emissivity * sideFaceFactor
					eqX = eqX + radMultiplier * (self.TAmb**4 - self.T**4) #fp.ImplicitSourceTerm(coeff = radMultiplier * self.T**3)
				# Perform iteration
				res = eqX.sweep(var = self.T, solver = solver, underRelaxation = self.solverSettings['relaxationFactor'])
				# Save residual
				self.resVector.append(res)
				# Save temperature and fluxes at the ends
				TFaces = self.T.arithmeticFaceValue()
				self.TLeft.append(TFaces[0])
				self.TRight.append(TFaces[-1])
				self.QLeft.append(self.QAx[0])
				self.QRight.append(self.QAx[-1])
							
				sweep += 1
		else:
			eqX.solve(var = self.T)
		
	
BoundaryConditionChoice = OrderedDict((
	('T', 'temperature'),
	('Q', 'heat flux')	
	))

class CryogenicPipe(NumericalModel):
	d_int = Quantity('Length', default = (5, 'mm'), label = 'internal diameter')
	d_ext = Quantity('Length', default = (10, 'mm'), label = 'external diameter')
	L = Quantity('Length', default = (1, 'm'), label = 'length')
	#thermalCond = Quantity('ThermalConductivity', default = 401, label = 'thermal conductivity')
	#emissivity = Quantity(default = 0.5, minValue = 0, maxValue=1.0, label = 'emissivity', show = 'self.computeRadiation')
	g1 = FieldGroup([d_int, d_ext, L], label = 'Pipe')
	
	bcLeft = Choices(BoundaryConditionChoice, label='boundary condition (left)')
	TLeftInput = Quantity('Temperature', default = (300, 'K'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeftInput = Quantity('HeatFlowRate', default = (0, 'W'), minValue = -1e99, maxValue = 1e99, 
			label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	bcRight = Choices(BoundaryConditionChoice, label='boundary condition (right)')
	TRightInput = Quantity('Temperature', default = (40, 'K'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRightInput = Quantity('HeatFlowRate', default = (0, 'W'), minValue = -1e99, maxValue = 1e99, 
			label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	computeRadiation = Boolean(default = True, label = 'compute radiation')
	TAmb = Quantity('Temperature', default = (300, 'K'), label = 'ambient temperature', show = 'self.computeRadiation')
	g2 = FieldGroup([bcLeft, TLeftInput, QLeftInput, bcRight, TRightInput, QRightInput, computeRadiation, TAmb], label = 'Boundary conditions')
	
	inputValues = SuperGroup([g1, g2], label = 'Input values')
	###
	n = Quantity(default = 50, minValue = 10, maxValue = 500, label = 'num. mesh elements')
	s1 = FieldGroup([n], label = 'Mesh')
	
	maxNumIter = Quantity(default = 100, minValue = 20, maxValue=500, label = 'max num. iterations')
	absTolerance = Quantity(default = 1e-6, label = 'absolute tolerance')
	relaxationFactor = Quantity(default = 0.99, maxValue = 2.0, label = 'relaxation factor')
	s2 = FieldGroup([maxNumIter, absTolerance, relaxationFactor], label = 'Solver')
	
	settings = SuperGroup([s1, s2], label = 'Settings')
	
	#####################
	
	Acs = Quantity('Area', default = (1, 'mm**2'), label = 'conduction area')
	As = Quantity('Area', default = (1, 'mm**2'), label = 'surface area')
	TLeft = Quantity('Temperature', label = 'temperature (left)')
	QLeft = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat flow (left)')
	TRight = Quantity('Temperature', label = 'temperature (right)')
	QRight = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat flow (right)')
	QRadSum = Quantity('HeatFlowRate', default = (1, 'W'), label = 'absorbed radiation')
	r1 = FieldGroup([Acs, As, TLeft, QLeft, TRight, QRight, QRadSum], label = 'Results') 
	r1g = SuperGroup([r1], label = 'Values')

	cond_T = PlotView(dataLabels = ['temperature [K]', 'thermal conductivity [W/m-K]'], options = {'title': 'Conductivity pipe', 'xlabel': 'temperature [K]', 'ylabel': 'thermal conductivity [W/m-K]'})
	emiss_T = PlotView(dataLabels = ['temperature [K]', 'emissivity [-]'], options = {'title': 'Emissivity', 'xlabel': 'temperature [K]', 'ylabel': 'emissivity[-]'})
	r2 = ViewGroup([cond_T, emiss_T], label = 'Material properties')
	r2g = SuperGroup([r2], label = 'Material properties')

	T_x = PlotView(dataLabels = ['x position [m]', 'temperature [K]'], options = {'title': 'Temperature', 'xlabel': 'x position [m]', 'ylabel': 'temperature [K]'})
	QAx_x = PlotView(dataLabels = ['x position [m]', 'heat flow [W]'], options = {'title': 'Axial heat flow', 'xlabel': 'x position [m]', 'ylabel': 'heat flow [W]'})
	QRad_x = PlotView(dataLabels = ['x position [m]', 'flux density [W/m]'], options = {'title': 'Radiation flux', 'xlabel': 'x position [m]', 'ylabel': 'flux density [W/m]'})
	cond_x = PlotView(dataLabels = ['x position [m]', 'thermal conductivity [W/m-K]'], options = {'title': 'Conductivity (pipe)', 'xlabel': 'x position [m]', 'ylabel': 'thermal conductivity [W/m-K]'})
	emiss_x = PlotView(dataLabels = ['x position [m]', 'emissivity [-]'], options = {'title': 'Emissivity', 'xlabel': 'x position [m]', 'ylabel': 'emissivity[-]'})
	table_x = TableView(dataLabels = ['x position [m]', 'temperature [K]', 'heat flow [W]'], options = {'title': 'Distributions (table)', 'formats': ['0.000', '0.00', '0.000E00'] })
	r3 = ViewGroup([T_x, QAx_x, QRad_x, cond_x, emiss_x, table_x], label =  'Distributions')
	r3g = SuperGroup([r3], label = 'Distributions')
	
	residualPlot = PlotView(dataLabels = ['iteration #', 'residual'], ylog = True, options = {'title': 'Residual'})
	residualTable = TableView(dataLabels = ['residual', 'TLeft', 'TRight'], options = {'title': 'Residual (table)', 'formats': ['0.0000E0', '0.000', '0.000']})
	r4 = ViewGroup([residualPlot, residualTable], label = 'Convergence')
	r4g = SuperGroup([r4], label = 'Convergence')
	
	results = [r1g, r2g, r3g, r4g]
	
	def compute(self):
		self.Acs = np.pi/4 * (self.d_ext * self.d_ext - self.d_int * self.d_int)
		self.As = np.pi * self.d_ext * self.L
		
		# Create the thermal model object
		model = ThermalModel1D(self.TAmb)
		#model.thermalCond = self.thermalCond
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
		
		model.solverSettings['nonlinear'] = True
		model.solverSettings['tolerance'] = self.absTolerance
		model.solverSettings['maxIterations'] = self.maxNumIter
		model.solverSettings['relaxationFactor'] = self.relaxationFactor
		model.solve()
		
		cellCenters = model.mesh.cellCenters.value[0]
		faceCenters = model.mesh.faceCenters.value[0]
		
		TRange = np.linspace(model.minT, model.maxT, num = 100)
		# Conduction vs. T
		self.cond_T = np.zeros((100, 2))
		self.cond_T[:, 0] = TRange
		self.cond_T[:, 1] = model.thermCondModel(TRange)
		# Emissivity vs. T
		self.emiss_T = np.zeros((100, 2))
		self.emiss_T[:, 0] = TRange
		self.emiss_T[:, 1] = model.emissivityModel(TRange)
		
		# Temperature distribution
		self.T_x = np.zeros((self.n + 1, 2))
		self.T_x[:, 0] = faceCenters 
		self.T_x[:, 1] = model.T.arithmeticFaceValue()
		self.TLeft = self.T_x[0, 1]
		self.TRight = self.T_x[-1, 1]
		
		# Axial heat flow
		self.QAx_x = np.zeros((self.n + 1, 2))
		self.QAx_x[:, 0] = faceCenters
		self.QAx_x[:, 1] = model.QAx()
		self.QLeft = self.QAx_x[0, 1]
		self.QRight = self.QAx_x[-1, 1]
		
		# Radiation flux
		self.QRad_x = np.zeros((self.n, 2))
		self.QRad_x[:, 0] = cellCenters
		self.QRad_x[:, 1] = model.QRad()
		self.QRadSum = self.QRight - self.QLeft
		
		# Conduction vs. x
		self.cond_x = np.zeros((self.n + 1, 2))
		self.cond_x[:, 0] = faceCenters
		self.cond_x[:, 1] = model.thermCond
		
		# Emissivity vs. x
		self.emiss_x = np.zeros((self.n, 2))
		self.emiss_x[:, 0] = cellCenters
		self.emiss_x[:, 1] = model.emissivity
		
		# Table with x distributions
		self.table_x = np.zeros((self.n + 1, 3))
		self.table_x[:, 0] = faceCenters
		self.table_x[:, 1] = model.T.arithmeticFaceValue()
		self.table_x[:, 2] = model.QAx
		
		# Convergence 
		numIter = len(model.resVector)
		self.residualPlot = np.zeros((numIter, 2))
		self.residualPlot[:, 0] = np.arange(numIter)
		self.residualPlot[:, 1] = model.resVector
		
		self.residualTable = np.zeros((numIter, 3))
		self.residualTable[:, 0] = model.resVector
		self.residualTable[:, 1] = model.TLeft
		self.residualTable[:, 2] = model.TRight
	
	@staticmethod
	def test():
		pipe = CryogenicPipe()
		pipe.compute()


		
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
if __name__ == '__main__':
	CryogenicPipe.test()