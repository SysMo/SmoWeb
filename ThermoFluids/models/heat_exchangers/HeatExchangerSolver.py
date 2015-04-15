import fipy as FP
import numpy as np
from smo.media.MaterialData import Solids
from smo.math.util import Interpolator1D
from fipy.solvers.pysparse import LinearLUSolver
from smo.flow.FrictionHeatExchange import FluidChannelSection, FluidChannel

class HeatExchangerSolver(object):
	def __init__(self, mesh, numPrimChannels, numSecChannels):
		self.blockMaterial= Solids['Aluminium6061']
		self.thermCondModel = Interpolator1D(
			self.blockMaterial['thermalCond_T']['T'], 
			self.blockMaterial['thermalCond_T']['cond'])
		# Solver settings
		self.solverSettings = {
			'tolerance': 1e-6,
			'maxIterations': 100,
			'relaxationFactor': 1.
		}
		self.linSolver = LinearLUSolver(tolerance = 1e-10)
		# Set the mesh
		self.mesh = mesh
		# Select the boundaries
		self.primChannels = self.mesh.physicalFaces['PrimaryChannel_1']
		for i in range(numPrimChannels - 1):
			self.primChannels |= self.mesh.physicalFaces['PrimaryChannel_%d'%(i + 2)]
		self.secChannels = self.mesh.physicalFaces['SecondaryChannel_1']
		for i in range(numSecChannels - 1):
			self.secChannels |= self.mesh.physicalFaces['SecondaryChannel_%d'%(i + 2)]
		self.extChannel = self.mesh.physicalFaces['OuterBoundary']
	
	def createChannelCalculators(self, heatExch):
		channelGeom = heatExch.channelGeom
		
		self.primChannelCalc = FluidChannel(heatExch.primaryFlow.fluidName)
		xStart = 0
		for geomSection in channelGeom.sections:
			dx = geomSection['length'] / geomSection['numDivisions']
			for i in range(geomSection['numDivisions']):
				section = FluidChannelSection(xStart + i * dx, xStart + (i + 1) * dx)
				section.setAnnularGeometry(geomSection['internalDiameter'], channelGeom.externalDiameter)
				self.primChannelCalc.addSection(section)
			xStart += geomSection['length']
		
		self.secChannelCalc = FluidChannel(heatExch.secondaryFlow.fluidName)
		xStart = 0
		for geomSection in channelGeom.sections:
			dx = geomSection['length'] / geomSection['numDivisions']
			for i in range(geomSection['numDivisions']):
				section = FluidChannelSection(xStart + i * dx, xStart + (i + 1) * dx)
				section.setAnnularGeometry(geomSection['internalDiameter'], channelGeom.externalDiameter)
				self.secChannelCalc.addSection(section)
			xStart += geomSection['length']
		
	def solve(self, heatExch):
		#TExt = 300
		# Create variables for temperature and thermal conductivity
		self.T = FP.CellVariable(name = 'T', mesh = self.mesh)
		self.thermCond = FP.FaceVariable(name = 'lambda', mesh = self.mesh)
		# Create the coefficient for the source terms emulating boundary conditions
		self.cPrimCoeff = (self.primChannels * self.mesh.faceNormals).divergence
		self.cSecCoeff = (self.secChannels * self.mesh.faceNormals ).divergence
		self.cExtCoeff = (self.extChannel * self.mesh.faceNormals ).divergence

		# Initial guess
		self.T.setValue(heatExch.externalFlow.TIn)
		# Solve for a single cross section
		for i in len(range(self.primChannelCalc.sections)):
			self.solveSectionThermal(
				TPrim = 100, hConvPrim = 2000, 
				TSec = 100, hConvSec = 0, 
				TExt = 300, hConvExt = 2000)
		self.checkResults(
			TPrim = 100, hConvPrim = 2000, 
			TSec = 100, hConvSec = 0, 
			TExt = 300, hConvExt = 2000)
	
	def solveSectionThermal(self, TPrim, hConvPrim, TSec, hConvSec, TExt, hConvExt):		
		# Run solverSettings
		
# 		from fipy.boundaryConditions.constraint import Constraint
# 		c1 = Constraint(TPrim, self.primChannels)
# 		c2 = Constraint(TExt, extChannels)
# 		self.T.constrain(c1)
# 		self.T.constrain(c2)
# 		self.thermCond.setValue(self.thermCondModel(TExt))
# 		eqT = FP.DiffusionTerm(coeff = self.thermCond)
# 		eqT.solve(var = self.T)
# 		self.T.release(constraint = c1)
# 		self.T.release(constraint = c2)
		
		# Initialize convergence criteria
		res = 1e10
		n = 0
		# Run the non-linear iteration loop
		while (res > self.solverSettings['tolerance'] and n < self.solverSettings['maxIterations']):
			# Interpolate temperature on faces
			TFaces = self.T.arithmeticFaceValue()
			# Compute thermal conductivity
			self.thermCond.setValue(self.thermCondModel(TFaces))		
			# Set up the equation
			## Diffusion term
			eqT = FP.DiffusionTerm(coeff = self.thermCond)
			## Source terms (implicit + explicit) emulating boundary conditions
			eqT += - FP.ImplicitSourceTerm(self.cPrimCoeff * hConvPrim) + self.cPrimCoeff * hConvPrim * TPrim
			eqT += - FP.ImplicitSourceTerm(self.cSecCoeff * hConvSec) + self.cSecCoeff * hConvSec * TSec
			eqT += - FP.ImplicitSourceTerm(self.cExtCoeff * hConvExt) + self.cExtCoeff * hConvExt * TExt
			# Linear solve
			res = eqT.sweep(var = self.T, solver = self.linSolver, underRelaxation = self.solverSettings['relaxationFactor'])
			print n, res
			n += 1

		# Update the boundary conditions		
		#hl = hConvPrim / self.getFaceAverage(var = self.thermCond, faceSelector = primaryChannels)
		#self.T.faceGrad.constrain([hl * self.T.faceValue - hl * TPrim], primaryChannels)
		#hl = hConvExt / self.getFaceAverage(var = self.thermCond, faceSelector = extChannels)
		#self.T.faceGrad.constrain([hl * self.T.faceValue - hl * TExt], extChannels)
	
	def checkResults(self, TPrim, hConvPrim, TSec, hConvSec, TExt, hConvExt):
		TFaces = self.T.arithmeticFaceValue()

		TPrimWall = self.getFaceAverage(TFaces, self.primChannels)
		TSecWall = self.getFaceAverage(TFaces, self.secChannels)
		TExtWall = self.getFaceAverage(TFaces, self.extChannel)
		
		QDotPrim = self.getFaceArea(self.primChannels) * hConvPrim * (TPrim - TPrimWall) 
		QDotSec = self.getFaceArea(self.secChannels) * hConvSec * (TSec - TSecWall) 
		QDotExt = self.getFaceArea(self.extChannel) * hConvExt * (TExt - TExtWall)
		
		print QDotPrim
		print QDotSec
		print QDotExt
		
		Q1 = np.sum((hConvPrim * (self.T - TPrim) * self.cPrimCoeff * self.mesh.cellVolumes).value)
		Q2 = np.sum((hConvSec * (self.T - TSec) * self.cSecCoeff * self.mesh.cellVolumes).value)
		QExt = np.sum((hConvExt * (self.T - TExt) * self.cExtCoeff * self.mesh.cellVolumes).value)
		
		print Q1
		print Q2
		print QExt
	
	def showResult(self):
		viewer = FP.Viewer(vars = [self.T], FIPY_VIEWER = 'mayavi')
		viewer.plotMesh()
		raw_input("Press <return> to proceed...") 

	def plotMesh(self):
		import pylab as plt
		import matplotlib.tri as tri
		vertexCoords = self.mesh.vertexCoords
		vertexIDs = self.mesh._orderedCellVertexIDs
		
		plt.figure(figsize=(8, 8))
		plotMesh = tri.Triangulation(vertexCoords[0], vertexCoords[1], np.transpose(vertexIDs))
		plt.triplot(plotMesh)
		plt.show()

	def getFaceAverage(self, var, faceSelector, mesh = None):
		if (mesh is None):
			mesh = self.mesh
		if (not isinstance(var, np.ndarray)):
			var = var.value
		value = np.sum(mesh.scaledFaceAreas[faceSelector.value] * var[faceSelector.value]) / \
			np.sum(mesh.scaledFaceAreas[faceSelector.value])
		return value	
	
	def getFaceArea(self, faceSelector):
		value = np.sum(self.mesh.scaledFaceAreas[faceSelector.value])
		return value
	
# 	def getFaceFlux(self, faceSelector):
# 		comp = (faceSelector * self.mesh.scaledFaceAreas *  self.thermCond).value * np.sum(self.mesh.faceNormals * self.T.faceGrad, axis = 0)
# 		value = np.sum(np.abs(comp))
# 		return value
		

if __name__ == '__main__':
	mesh1 = FP.Gmsh2D(open('CylindricalHeatExchanger1.geo').read())
	solver = HeatExchangerSolver(mesh = mesh1)
	print "Num cells: %d"%len(solver.mesh.cellCenters()[0])

	solver.solve()
	#solver.plotMesh()
	solver.showResult()
	print solver.T
