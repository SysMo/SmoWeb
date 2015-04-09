'''
Created on Nov 30, 2014

@author: Atanas Pavlov
@copyright: SysMo Ltd.
'''

import numpy as np
from collections import OrderedDict
import fipy as fp
from fipy.solvers.pysparse import LinearLUSolver
from scipy.interpolate import interp1d
import smo.math.util as sm

sigmaSB = 5.67e-8

class DictObject(object):
	def __init__(self, **kwargs):
		for key, value in kwargs.iteritems():
			self.__dict__[key] = value

class CryogenicPipeSolver(object):
	def __init__(self, TAmb, thermalConductivityModel):
		self.BCs = (None, None)
		self.TAmb = TAmb
		self.conduction = {
			'model': thermalConductivityModel
		}
		self.radiation = {
			'active' : False,
		}
		self.solverSettings = {
			'nonlinear': False,
			'tolerance': 1e-8,
			'maxIterations': 1000,
			'relaxationFactor': 1.0
		}
		
	def createLinearMesh(self, sections, Acs, As): 
		""" Define mesh """
		# Cross sectional area
		self.AcsMult = Acs
		# Area multiplier for face area
		self.areaMult = Acs
		# Surface area per unit length
		self.As = As
		# Create the meshes and emissivity calculator for each segment
		self.emissivityCalculator = sm.SectionCalculator()
		dx = []		
		i = 0
		for sec in sections:
			numElements = np.ceil(sec['length'] / sec['meshSize'])			
			self.emissivityCalculator.addSection(
					(i, i + numElements - 1), 
					sm.Interpolator1D([sec['temperature1'], sec['temperature2']], [sec['emissivity1'], sec['emissivity2']])
			)
			dx += [sec['length'] / numElements] * numElements
			i += numElements
		self.radiation['emissivity'] = np.zeros((len(dx)))
		self.mesh = fp.Grid1D(dx = dx)
		self.meshType = 'Linear'
		# Define variable
		self.T = fp.CellVariable(name = "temperature",
			mesh = self.mesh, value = 0.)
		self.thermCond = fp.FaceVariable(mesh = self.mesh)
		self.emissivity = fp.CellVariable(mesh = self.mesh)
	
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
		return np.min(self.T.arithmeticFaceValue())
	@property
	def maxT(self):
		return np.max(self.T.arithmeticFaceValue())


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
			gradValue = value / faceArea / self.thermalConductivity
			self.T.faceGrad.constrain([-gradValue], face)
		else:
			raise ValueError('BC type must be T(temperature) or Q(heat flux)')
		
	def solve(self):
		sideFaceFactor = fp.CellVariable(name = "sideFaceFactor",
			mesh = self.mesh, value = self.sideFaceAreas / (self.areaMult * self.mesh.cellVolumes))

		# Initial conditions
		self.T.setValue(self.TAmb)
		# Run solverSettings
		solver = LinearLUSolver(tolerance=1e-10)
		if (self.solverSettings['nonlinear']):
			res = 1
			sweep = 0
			self.resVector = []
			TFaces = self.T.arithmeticFaceValue()
			self.TLeft = []
			self.TRight = []
			self.QLeft = []
			self.QRight = []
			while (res > self.solverSettings['tolerance'] and sweep < self.solverSettings['maxIterations']):
				# Compute temperature dependent thermal conductivity 
				self.thermCond.setValue(self.conduction['model'](TFaces))
				# Add the conductivity term to the equation					
				eqX = fp.DiffusionTerm(coeff = self.thermCond)
				if (self.radiation['active']):
					# Compute temperature dependent emissivity
					self.emissivity.setValue(self.emissivityCalculator(self.T()))
					# Add radiation term to the equation
					radMultiplier = sigmaSB * self.emissivity * sideFaceFactor
					eqX = eqX + radMultiplier * (self.TAmb**4 - self.T**4)
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
		
	
from smo.model.model import NumericalModel
from smo.model.fields import *
from smo.model.actions import ServerAction, ActionBar
from smo.media.MaterialData import Solids

BoundaryConditionChoice = OrderedDict((
	('T', 'temperature'),
	('Q', 'heat flux')	
	))

class CryogenicPipe(NumericalModel):
	"""
	1D Solver for heat flow of an insulated cryogenic pipe in vacuum. The
	processes modelled are:
	
		* conduction along the pipe
		* ambient radiation to the pipe surface
	"""
	label = "Cryogenic Pipe"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/CryogenicPipe.svg")
	description = ModelDescription("1D thermal solver for heat flow of an insulated cryogenic \
	pipe in vacuum. Accounts for conduction along the pipe and ambient radiation to the \
	pipe surface. The material can have temperature dependent  properties", show = True)
	
	# 1. ############ Inputs ###############
	# 1.1 Input values
	d_int = Quantity('Length', default = (5, 'mm'), label = 'internal diameter')
	d_ext = Quantity('Length', default = (10, 'mm'), label = 'external diameter')
	sections = RecordArray((
								('length', Quantity('Length', default = (1, 'm'), label = 'length')),
								('emissivity1', Quantity(default = 0.036, label = 'emissivity 1')),
								('temperature1', Quantity('Temperature', default = (40, 'K'), label = 'temperature 1')),
								('emissivity2', Quantity(default = 0.1385, label = 'emissivity 2')),
								('temperature2', Quantity('Temperature', default = (288, 'K'), label = 'temperature 2')),
								('meshSize', Quantity('Length', default = (5, 'mm'), label = 'meshSize')),
							), label = 'sections')
	pipeMaterial = ObjectReference(Solids, default = 'StainlessSteel304', label = 'pipe material')
	g1 = FieldGroup([d_int, d_ext, sections, pipeMaterial], label = 'Pipe')
	
	bcLeft = Choices(BoundaryConditionChoice, label='boundary condition (left)')
	TLeftInput = Quantity('Temperature', default = (288, 'K'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeftInput = Quantity('HeatFlowRate', default = (0, 'W'), minValue = -1e99, maxValue = 1e99, 
			label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	bcRight = Choices(BoundaryConditionChoice, label='boundary condition (right)')
	TRightInput = Quantity('Temperature', default = (40, 'K'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRightInput = Quantity('HeatFlowRate', default = (0, 'W'), minValue = -1e99, maxValue = 1e99, 
			label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	computeRadiation = Boolean(default = True, label = 'compute radiation')
	TAmb = Quantity('Temperature', default = (288, 'K'), label = 'ambient temperature', show = 'self.computeRadiation')
	g2 = FieldGroup([bcLeft, TLeftInput, QLeftInput, bcRight, TRightInput, QRightInput, computeRadiation, TAmb], label = 'Boundary conditions')
	
	inputValues = SuperGroup([g1, g2], label = 'Input values')
	
	# 1.2 Settings
	maxNumIter = Quantity(default = 100, minValue = 20, maxValue=500, label = 'max num. iterations')
	absTolerance = Quantity(default = 1e-6, label = 'absolute tolerance')
	relaxationFactor = Quantity(default = 0.99, maxValue = 2.0, label = 'relaxation factor')
	s1 = FieldGroup([maxNumIter, absTolerance, relaxationFactor], label = 'Solver')
	
	testPoints = RecordArray((
								('xPosition',  Quantity('Length', label = 'x position')),
							), label = 'test points')
	s2 = FieldGroup([testPoints], label = 'Post-processing')

	settings = SuperGroup([s1, s2], label = 'Settings')

	# 1.3 Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# 1.4 Model view
	inputView = ModelView(ioType = "input", superGroups = [inputValues, settings], 
		actionBar = inputActionBar, autoFetch = True)

	# 2. ############ Results ###############
	# 2.1 Values
	AcsMult = Quantity('Area', default = (1, 'mm**2'), label = 'conduction area')
	As = Quantity('Length', default = (1, 'm'), label = 'surface area / length')
	TLeft = Quantity('Temperature', label = 'temperature (left)')
	QLeft = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat flow (left)')
	TRight = Quantity('Temperature', label = 'temperature (right)')
	QRight = Quantity('HeatFlowRate', default = (1, 'W'), label = 'heat flow (right)')
	QRadSum = Quantity('HeatFlowRate', default = (1, 'W'), label = 'absorbed radiation')
	r1 = FieldGroup([AcsMult, As, TLeft, QLeft, TRight, QRight, QRadSum], label = 'Results') 
	r1g = SuperGroup([r1], label = 'Values')

	# 2.2 Distributions
	T_x = PlotView((
                    ('x position', Quantity('Length', default=(1, 'm'))),
                    ('temperature', Quantity('Temperature', default=(1, 'K'))),
                	),
					label = 'Temperature')
	QAx_x = PlotView((
	                    ('x position', Quantity('Length', default=(1, 'm'))),
	                    ('heat flow', Quantity('HeatFlowRate', default=(1, 'W'))),
	                	),
						label = 'Axial heat flow')
	QRad_x = PlotView((
                        ('x position', Quantity('Length', default=(1, 'm'))),
                        ('flux density', Quantity('LinearHeatFluxDensity', default=(1, 'W/m'))),
                    	),
						label = 'Radiation flux')
	cond_x = PlotView((
                        ('x position', Quantity('Length', default=(1, 'm'))),
                        ('thermal conductivity', Quantity('ThermalConductivity', default=(1, 'W/m-K'))),
                    	),
						label = 'Conductivity (pipe)')
	emiss_x = PlotView((
                        ('x position', Quantity('Length', default=(1, 'm'))),
                        ('emissivity', Quantity('Dimensionless'))
                    	),
						label = 'Emissivity')
	table_x = TableView((
	                        ('x position', Quantity('Length')),
	                        ('temperature', Quantity('Temperature')),
	                        ('heat flow', Quantity('HeatFlowRate')),
	                    	),
							label = 'Distributions (table)',
							options = {'formats': ['0.000', '0.00', '0.000E00'] })
	testPointResults = TableView((
		                            ('x position', Quantity('Length')),
		                            ('temperature', Quantity('Temperature'))
		                        	),
								label = 'Test points',
								options = {'formats': ['0.000', '0.00']}) 
	r2 = ViewGroup([T_x, QAx_x, QRad_x, cond_x, emiss_x, table_x, testPointResults], label =  'Distributions')
	r2g = SuperGroup([r2], label = 'Distributions')
	
	# 2.2 Material properties
	cond_T = PlotView((
                        ('temperature', Quantity('Temperature', default=(1, 'K'))),
                        ('thermal conductivity', Quantity('ThermalConductivity', default=(1,'W/m-K')))
                    	),
						label = 'Conductivity pipe')
	#emiss_T = PlotView(label = 'Emissivity', dataLabels = ['temperature [K]', 'emissivity [-]'])
	r3 = ViewGroup([cond_T], label = 'Material properties')
	r3g = SuperGroup([r3], label = 'Material properties')

	# 2.4 Residuals 
	residualPlot = PlotView((
	                            ('iteration #', Quantity('Dimensionless')),
	                            ('residual', Quantity('Dimensionless'))
	                        	),
								label = 'Residual (plot)', ylog = True)
	residualTable = TableView((
	                            ('residual', Quantity('Dimensionless')),
	                            ('TLeft', Quantity('Temperature')),
	                            ('TRight', Quantity('Temperature')),
	                        	),
								label = 'Residual (table)',
								options = {'formats': ['0.0000E0', '0.000', '0.000']})
	r4 = ViewGroup([residualPlot, residualTable], label = 'Convergence')
	r4g = SuperGroup([r4], label = 'Convergence')
	
	# 2.5 Model view
	resultView = ModelView(ioType = "output", superGroups = [r1g, r2g, r3g, r4g])

	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	############# Methods ###############
	def compute(self):
		# Initial checks
		if ('thermalCond_T' not in Solids[self.pipeMaterial['_key']]):
			raise ValueError("Material {0} doesn't have a model for temperature-dependent conductivity".format(self.pipeMaterial['label']))
			
		self.AcsMult = np.pi/4 * (self.d_ext * self.d_ext - self.d_int * self.d_int)
		self.As = np.pi * self.d_ext
		
		# Create the thermal solver object and set the object calculating thermal conductivity
		model = CryogenicPipeSolver(self.TAmb, 
			thermalConductivityModel = interp1d(self.pipeMaterial['thermalCond_T']['T'], self.pipeMaterial['thermalCond_T']['cond'])
		)
		# Create mesh
		model.createLinearMesh(sections = self.sections, Acs = self.AcsMult, As = self.As)
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
		self.cond_T[:, 1] = model.conduction["model"](TRange)
		# Emissivity vs. T
#		self.emiss_T = np.zeros((100, 2))
#		self.emiss_T[:, 0] = TRange
#		self.emiss_T[:, 1] = model.emissivityModel(TRange)
		
		# Temperature distribution
		self.T_x = np.zeros((len(faceCenters), 2))
		self.T_x[:, 0] = faceCenters 
		self.T_x[:, 1] = model.T.arithmeticFaceValue()
		self.TLeft = self.T_x[0, 1]
		self.TRight = self.T_x[-1, 1]
		
		# Axial heat flow
		self.QAx_x = np.zeros((len(faceCenters), 2))
		self.QAx_x[:, 0] = faceCenters
		self.QAx_x[:, 1] = model.QAx()
		self.QLeft = self.QAx_x[0, 1]
		self.QRight = self.QAx_x[-1, 1]
		
		# Radiation flux
		self.QRad_x = np.zeros((len(cellCenters), 2))
		self.QRad_x[:, 0] = cellCenters
		self.QRad_x[:, 1] = model.QRad()
		self.QRadSum = self.QRight - self.QLeft
			
		# Conduction vs. x
		self.cond_x = np.zeros((len(faceCenters), 2))
		self.cond_x[:, 0] = faceCenters
		self.cond_x[:, 1] = model.thermCond
		
		# Emissivity vs. x
		self.emiss_x = np.zeros((len(cellCenters), 2))
		self.emiss_x[:, 0] = cellCenters
		self.emiss_x[:, 1] = model.emissivity
		
		# Table with x distributions
		self.table_x = np.zeros((len(faceCenters), 3))
		self.table_x[:, 0] = faceCenters
		self.table_x[:, 1] = model.T.arithmeticFaceValue()
		self.table_x[:, 2] = model.QAx
		
		# Table with test points
		self.testPointResults = np.zeros((len(self.testPoints), 2))
		self.testPointResults[:, 0] = self.testPoints['xPosition']
		self.testPointResults[:, 1] = model.T((self.testPoints['xPosition'],))
		
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
