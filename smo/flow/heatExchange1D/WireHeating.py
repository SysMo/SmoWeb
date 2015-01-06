'''
Created on Dec 15, 2014

@author: Atanas Pavlov
@copyright: SysMo Ltd.
'''
import numpy as np
from smo.model.model import NumericalModel
from smo.model.fields import *
from smo.media.SimpleMaterials import Solids
from collections import OrderedDict
import fipy as fp
from fipy.solvers.pysparse import LinearLUSolver

sigmaSB = 5.67e-8

class WireHeatingSolver(object):
	def __init__(self, thermalConductivity, TAmb, Acs, AExtMult):
		self.TAmb = TAmb
		self.AcsMult = Acs
		self.AExtMult = AExtMult
		self.thermalConductivity = thermalConductivity
		self.jouleHeating = {
			'active': False,
			'eResistivity': 1.0,
			'j': 1.0
		}
		self.convection = {
			'active': False,
			'coefficient': 1.0,
		}
		self.insulation = {
			'active': False,
			'thickness': 1.0,
			'thermConductivity': 0
		}
		self.radiation = {
			'active': False,
			'emissivity': 0.9,
		}
		self.solverSettings = {
			'nonlinear': False,
			'tolerance': 1e-6,
			'maxIterations': 50,
			'relaxationFactor': 0.99
		}
		self.BC = [
			{'type': 'Q', 'flux': 0},
			{'type': 'Q', 'flux': 0},
		]

	def createLinearMesh(self, L, n = 100): 
		""" Creates 1D mesh """
		dx = float(L) / n
		self.mesh = fp.Grid1D(nx = n, dx = dx)
		self.meshType = 'Linear'

	@property
	def areaExtFaces(self):
		faceCenters = self.mesh.faceCenters()[0]
		faceAreas = self.AExtMult * (faceCenters[1:] - faceCenters[:-1])
		return faceAreas
	
	@property
	def QAx(self):
		return fp.FaceVariable(mesh = self.mesh, 
			value = - self.thermalConductivity * self.AcsMult * self.mesh.scaledFaceAreas * self.TCore.faceGrad)	
	
	@property
	def QRad(self):
		if (self.radiation['active']):
			value = sigmaSB * self.radiation['emissivity'] * self.AExtMult * (self.TSurface()**4 - self.TAmb**4)
		else:
			value = np.zeros(self.TSurface().shape)
		return value	
	
	@property
	def QRadSum(self):
		return np.sum(self.QRad * np.diff(self.mesh.faceCenters()))

	@property
	def QConv(self):
		if (self.convection['active']):
			value = self.convection['coefficient'] * self.AExtMult * (self.TSurface() - self.TAmb)
		else:
			value = np.zeros(self.TSurface().shape)
		return value

	@property
	def QConvSum(self):
		return np.sum(self.QConv * np.diff(self.mesh.faceCenters()))

	@property
	def QJouleSum(self):
		if (self.jouleHeating['active']):
			value = self.jouleHeating['j']**2 * self.jouleHeating['eResistivity'] * self.AcsMult * np.sum(self.mesh.cellVolumes)
		else:
			value = 0
		return value

	@property
	def maxT(self):
		return np.max(self.TCore.arithmeticFaceValue())

	def applyBC(self, faces, bcDef, area = None):
		if (bcDef['type'] == 'T'):
			self.TCore.constrain(bcDef['temperature'], faces)
		elif (bcDef['type'] == 'Q'):
			gradValue = bcDef['flux'] / area / self.thermalConductivity
			self.TCore.faceGrad.constrain([-gradValue], faces)			
		else:
			raise NotImplementedError('Boundary conditions type "{0}" is not implemented'.format(bcDef[type]))
		
	def solve(self):
		sideFaceFactor = fp.CellVariable(name = "sideFaceFactor",
			mesh = self.mesh, value = self.areaExtFaces / (self.AcsMult * self.mesh.cellVolumes))
		# Create variables
		self.TCore = fp.CellVariable(name = "coreTemperature",
			mesh = self.mesh, value = self.TAmb)
		self.TSurface = fp.CellVariable(name = "surfaceTemperature",
			mesh = self.mesh, value = self.TAmb)
		# Apply boundary conditions:
		self.applyBC(self.mesh.facesLeft(), self.BC[0], self.mesh.scaledFaceAreas[0] * self.AcsMult)
		self.applyBC(self.mesh.facesRight(), self.BC[1], self.mesh.scaledFaceAreas[-1] * self.AcsMult)
		
		# Create linear solver
		linSolver = LinearLUSolver(tolerance = 1e-10)
		
		# Create base equation (thermal conduction):
		eq = fp.DiffusionTerm(coeff = self.thermalConductivity, var = self.TCore)
		if (self.jouleHeating['active']):
			eq += self.jouleHeating['j']**2  * self.jouleHeating['eResistivity']
		
		if (self.radiation['active']):
			raise NotImplementedError('Radiation not implemented yet!')
		else:
			if (self.convection['active']):
				RAmb = 1. / self.convection['coefficient']
				if (self.insulation['active']):
					RAmb += self.insulation['thickness'] / self.insulation['thermConductivity']
				eq += 1. / RAmb * (sideFaceFactor * self.TAmb - fp.ImplicitSourceTerm(coeff = sideFaceFactor, var = self.TCore))
			eq.solve(var = self.TCore, solver = linSolver)
			if (self.convection['active'] and self.insulation['active']):
				# 0 - limited by conduction, 1 - limited by convection 
				a1 = 1. / (RAmb * self.convection['coefficient'])				
				self.TSurface.setValue(a1 * self.TCore() + (1 - a1) * self.TAmb)
				print a1
			else:
				self.TSurface.setValue(self.TCore())

BoundaryConditionChoice = OrderedDict((
	('T', 'temperature'),
	('Q', 'heat flux'),
	('R', 'resistive heating')
	))

class CableHeating1D(NumericalModel):
	d = Quantity('Length', default = (2, 'mm'), label = 'diameter')
	L = Quantity('Length', default = (1, 'm'), label = 'length')
	thermalConductivity = Quantity('ThermalConductivity', default = Solids['Copper']['refValues']['tConductivity'], label = 'cable thermal conductivity')
	eResistivity = Quantity('ElectricalResistivity', default = Solids['Copper']['refValues']['eResistivity'], label = 'cable electrical resistivity')
	I = Quantity('ElectricalCurrent', default = (10, 'A'), label = 'electrical current')
	hasInsulation = Boolean(default = False, label = 'cable insulated')
	insulation_thickness = Quantity('Length', default = (1, 'mm'), label = 'insulation thickness', show = 'self.hasInsulation')
	insulation_thermalCond = Quantity('ThermalConductivity', default = Solids['Polyvinylchloride']['refValues']['tConductivity'], 
					label = 'insulation th. conductivity', show = 'self.hasInsulation')
	g1 = FieldGroup([d, L, thermalConductivity, eResistivity, I, hasInsulation, insulation_thickness, insulation_thermalCond], label = 'Cable')
	
	bcLeft = Choices(BoundaryConditionChoice, label='boundary condition (left)')
	TLeftInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeftInput = Quantity('HeatFlowRate', default = (0, 'W'), minValue = -1e99, maxValue = 1e99, 
			label = 'heat entering (left)', show = 'self.bcLeft == "Q"')
	hLeftDissipation = Quantity('ThermalConductance', default = (0, 'W/K'), minValue = 0, 
			label = 'local dissipation (left)', show = 'self.bcLeft == "Q"')
	bcRight = Choices(BoundaryConditionChoice, label='boundary condition (right)')
	TRightInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRightInput = Quantity('HeatFlowRate', default = (0, 'W'), minValue = -1e99, maxValue = 1e99, 
			label = 'heat entering (right)', show = 'self.bcRight == "Q"')
	hRightDissipation = Quantity('ThermalConductance', default = (0, 'W/K'), minValue = 0, 
			label = 'local dissipation (left)', show = 'self.bcRight == "Q"')
	computeRadiation = Boolean(default = False, label = 'compute radiation')
	computeConvection = Boolean(default = True, label = 'compute convection')
	TAmb = Quantity('Temperature', default = (20, 'degC'), label = 'ambient temperature', show = 'self.computeRadiation || self.computeConvection')
	convCoeff = Quantity('HeatTransferCoefficient', default = (10, 'W/m**2-K'), label = 'convection coefficient', 
				show = "self.computeConvection")	
	emissivity = Quantity(default = 0.9, minValue = 0, maxValue = 1, label = 'surface emissivity', 
				show = "self.computeRadiation")	
	g2 = FieldGroup([bcLeft, TLeftInput, QLeftInput, hLeftDissipation, bcRight, TRightInput, QRightInput, hRightDissipation, 
					computeRadiation, computeConvection, TAmb, convCoeff, emissivity], label = 'Boundary conditions')
	
	inputValues = SuperGroup([g1, g2], label = "Input values")
	###
	n = Quantity(default = 50, minValue = 10, maxValue = 500, label = 'num. mesh elements')
	s1 = FieldGroup([n], label = 'Mesh')
	
	maxNumIter = Quantity(default = 100, minValue = 20, maxValue=500, label = 'max num. iterations')
	absTolerance = Quantity(default = 1e-6, label = 'absolute tolerance')
	relaxationFactor = Quantity(default = 0.99, maxValue = 2.0, label = 'relaxation factor')
	s2 = FieldGroup([maxNumIter, absTolerance, relaxationFactor], label = 'Solver')
	
	settings = SuperGroup([s1, s2], label = 'Settings')
 	inputs = [inputValues, settings]
	#####################
	Acs = Quantity('Area', default = (1, 'mm**2'), label = 'conduction area')
	As = Quantity('Length', default = (1, 'm'), label = 'surface area / length')
	TLeft = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)')
	QLeft = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat entering (left)')
	TRight = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (right)')
	QRight = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat entering (right)')
	QRadSum = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat emitted (radiation)')
	QConvSum = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat emitted (convection)')
	QJouleSum = Quantity('HeatFlowRate', default = (1, 'W'), label = 'joule heating')
	r11 = FieldGroup([TLeft, QLeft, TRight, QRight, QRadSum, QConvSum, QJouleSum], label = 'Temperatures & fluxes') 
	r12 = FieldGroup([Acs, As], label = 'Miscellaneous') 
	r1g = SuperGroup([r11, r12], label = 'Values')

	T_x = PlotView(label = 'Temperatures', dataLabels = ['x position [m]', 'core temperature [degC]', 'surface temperature [degC]'],
				options = {'ylabel': 'temperature [degC]'})
	QAx_x = PlotView(label = 'Axial heat flow', dataLabels = ['x position [m]', 'heat flow [W]'])
	QConv_x = PlotView(label = 'Convection flux', dataLabels = ['x position [m]', 'flux density [W/m]'])
	QRad_x = PlotView(label = 'Radiation flux', dataLabels = ['x position [m]', 'flux density [W/m]'])
	table_x = TableView(label = 'Distributions (table)', dataLabels = ['x position [m]', 'temperature [K]', 'heat flow [W]'],
			options = {'formats': ['0.000', '0.00', '0.000E00'] })
	r3 = ViewGroup([T_x, QAx_x, QConv_x, QRad_x, table_x], label =  'Distributions')
	r3g = SuperGroup([r3], label = 'Distributions')
	
	residualPlot = PlotView(label = 'Residual (plot)', dataLabels = ['iteration #', 'residual'], ylog = True)
	residualTable = TableView(label = 'Residual (table)', dataLabels = ['residual', 'TLeft', 'TRight'], 
			options = {'formats': ['0.0000E0', '0.000', '0.000']})
	r4 = ViewGroup([residualPlot, residualTable], label = 'Convergence')
	r4g = SuperGroup([r4], label = 'Convergence')
	
	results = [r1g, r3g, r4g]

	
	def compute(self):
		self.Acs = np.pi/4 * self.d * self.d
		self.As = np.pi * self.d
		
		## Create the thermal model object
		model = WireHeatingSolver(thermalConductivity = self.thermalConductivity, 
			TAmb = self.TAmb, Acs = self.Acs, AExtMult = self.As)
		## Create mesh
		model.createLinearMesh(L = self.L, n = self.n)
		## Set boundary conditions
		if (self.bcLeft == 'T'):
			model.BC[0]['type'] = 'T'
			model.BC[0]['temperature'] = self.TLeftInput
		else:
			model.BC[0]['type'] = 'Q'
			model.BC[0]['flux'] = self.QLeftInput

		if (self.bcRight == 'T'):
			model.BC[-1]['type'] = 'T'
			model.BC[-1]['temperature'] = self.TRightInput
		else:
			model.BC[-1]['type'] = 'Q'
			model.BC[-1]['flux'] = - self.QRightInput
				
# 		self.convection = {
# 			'active': False,
# 			'coefficient': 1.0,
# 		}
# 		self.solverSettings = {
# 			'nonlinear': False,
# 			'tolerance': 1e-6,
# 			'maxIterations': 50,
# 			'relaxationFactor': 0.99
# 		}
		
		## Models and model settings
		# Joule heating
		model.jouleHeating['active'] = True
		model.jouleHeating['eResistivity'] = self.eResistivity
		model.jouleHeating['j'] = self.I / self.Acs
		# Insulation settings
		if (self.hasInsulation):
			model.insulation['active'] = True
			model.insulation['thickness'] = self.insulation_thickness
			model.insulation['thermConductivity'] = self.insulation_thermalCond
		# Convection settings
		if (self.computeRadiation):
			model.radiation['active'] = True
			model.radiation['emissivity'] = self.emissivity
		# Radiation settings
		if (self.computeConvection):
			model.convection['active'] = True 
			model.convection['coefficient'] = self.convCoeff
		
		## Solve
		model.solve()
		
		## Postprocessing
		cellCenters = model.mesh.cellCenters.value[0]
		faceCenters = model.mesh.faceCenters.value[0]
			
		# Temperature distribution
		self.T_x = np.zeros((self.n + 1, 3))
		self.T_x[:, 0] = faceCenters 
		self.T_x[:, 1] = model.TCore.arithmeticFaceValue() - 273.15
		self.T_x[:, 2] = model.TSurface.arithmeticFaceValue() - 273.15
		self.TLeft = (self.T_x[0, 1], 'degC')
		self.TRight = (self.T_x[-1, 1], 'degC')
		
		# Axial heat flow
		self.QAx_x = np.zeros((self.n + 1, 2))
		self.QAx_x[:, 0] = faceCenters
		self.QAx_x[:, 1] = model.QAx
		self.QLeft = self.QAx_x[0, 1]
		self.QRight = - self.QAx_x[-1, 1]
		
		# Convection flux
		self.QConv_x = np.zeros((self.n, 2))
		self.QConv_x[:, 0] = cellCenters
		self.QConv_x[:, 1] = model.QConv

		# Radiation flux
		self.QRad_x = np.zeros((self.n, 2))
		self.QRad_x[:, 0] = cellCenters
		self.QRad_x[:, 1] = model.QRad
		
		# Integral heats
		self.QConvSum = model.QConvSum
		self.QRadSum = model.QRadSum
		self.QJouleSum = model.QJouleSum
		
		# Table with x distributions
		self.table_x = np.zeros((self.n + 1, 3))
		self.table_x[:, 0] = faceCenters
		self.table_x[:, 1] = model.TCore.arithmeticFaceValue()
		self.table_x[:, 2] = model.QAx