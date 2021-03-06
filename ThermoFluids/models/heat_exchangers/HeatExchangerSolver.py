import fipy as FP
import numpy as np
from smo.media.MaterialData import Solids
from smo.math.util import Interpolator1D
from fipy.solvers.pysparse import LinearLUSolver
from smo.flow.FrictionHeatExchange import FluidChannelSection, FluidChannel
from smo.media.CoolProp.CoolProp import FluidState
from fipy.viewers import Matplotlib2DViewer
import uuid
import os
from SmoWeb.settings import MEDIA_ROOT
from matplotlib.colors import Normalize
import matplotlib.colorbar as colorbar 
import matplotlib.cm as cm

class HeatExchangerSolver(object):
	def __init__(self, heatExch, mesher):
		self.blockMaterial= heatExch.blockProps.material
		self.thermCondModel = Interpolator1D(
			self.blockMaterial['thermalCond_T']['T'], 
			self.blockMaterial['thermalCond_T']['cond'])
		# Solver settings
		self.fvSolverSettings = heatExch.fvSolverSettings
		self.linSolver = LinearLUSolver(tolerance = 1e-10)
		# Set the mesh
		self.mesh = mesher.mesh
		# Select the boundaries
		self.primChannels = self.mesh.physicalFaces['PrimaryChannel_1']
		for i in range(heatExch.primaryChannelsGeom.number - 1):
			self.primChannels |= self.mesh.physicalFaces['PrimaryChannel_%d'%(i + 2)]
		self.secChannels = self.mesh.physicalFaces['SecondaryChannel_1']
		for i in range(heatExch.secondaryChannelsGeom.number - 1):
			self.secChannels |= self.mesh.physicalFaces['SecondaryChannel_%d'%(i + 2)]
		self.extChannel = self.mesh.physicalFaces['OuterBoundary']
		self.numPlots = 5
		self.currPlot = 1
		self.lastPlotPos = -1
		
	def createChannelCalculators(self, heatExch):		
		# Setup the two calculators for each set of channels
		self.primChannelCalc = FluidChannel(heatExch.primaryFlowIn.createFluidState)
		self.secChannelCalc = FluidChannel(heatExch.secondaryFlowIn.createFluidState)
		self.extChannelCalc = FluidChannel(heatExch.externalFlowIn.createFluidState)
		self.primChannelStateOut = heatExch.primaryFlowIn.createFluidState()
		self.secChannelStateOut = heatExch.secondaryFlowIn.createFluidState()
		self.extChannelStateOut = heatExch.externalFlowIn.createFluidState()
		# Starting position of sections
		primChannelSectionsX = np.cumsum(heatExch.primaryChannelsGeom.sections['length'])
		secChannelSectionsX = np.cumsum(heatExch.secondaryChannelsGeom.sections['length'])
		# Check if channels have correct length
		if (abs(primChannelSectionsX[-1] - heatExch.blockGeom.length) > 1e-6):
			raise ValueError('The sum of the length of the primary channel sections (%g m) is not\
				 equal to the total length of the heat exchanger (%g m)' % (primChannelSectionsX[-1], heatExch.blockGeom.length))
		if (abs(secChannelSectionsX[-1] - heatExch.blockGeom.length) > 1e-6):
			raise ValueError('The sum of the length of the primary channel sections (%g m) is not\
				 equal to the total length of the heat exchanger (%g m)' % (secChannelSectionsX[-1], heatExch.blockGeom.length))
		# Create the sections of the channel		
		primSectionIndex = 0
		secSectionIndex = 0
		self.stepX = heatExch.blockProps.divisionStep
		secStartX = np.arange(0, heatExch.blockGeom.length, self.stepX)
		self.numSectionSteps = len(secStartX)
		for x in secStartX:
			# primary
			if (x > primChannelSectionsX[primSectionIndex]):
				primSectionIndex += 1
			primSection = FluidChannelSection(x, x + self.stepX)
			primSection.setAnnularGeometry(
					dIn = heatExch.primaryChannelsGeom.sections[primSectionIndex]['internalDiameter'], 
					dOut = heatExch.primaryChannelsGeom.externalDiameter)
			self.primChannelCalc.addSection(primSection)
			# secondary
			if (x > secChannelSectionsX[secSectionIndex]):
				secSectionIndex += 1
			secSection = FluidChannelSection(x, x + self.stepX)
			secSection.setAnnularGeometry(
					dIn = heatExch.secondaryChannelsGeom.sections[secSectionIndex]['internalDiameter'], 
					dOut = heatExch.secondaryChannelsGeom.externalDiameter)
			self.secChannelCalc.addSection(secSection)
			# external
			extSection = FluidChannelSection(x, x + self.stepX)
			extSection.setHelicalGeometry_RectChannel(
					axialWidth = heatExch.externalChannelGeom.widthAxial, 
					radialHeight = heatExch.externalChannelGeom.heightRadial, 
					Dw = heatExch.externalChannelGeom.averageCoilDiameter,
					pitch = heatExch.externalChannelGeom.coilPitch
			)
			self.extChannelCalc.addSection(extSection)
			
		self.primChannelCalc.setMDot(heatExch.primaryFlowIn.mDot / heatExch.primaryChannelsGeom.number)
		self.secChannelCalc.setMDot(heatExch.secondaryFlowIn.mDot / heatExch.secondaryChannelsGeom.number)
		self.extChannelCalc.setMDot(heatExch.externalFlowIn.mDot)

	def solve(self, heatExch):
		# Create variables for temperature and thermal conductivity
		self.T = FP.CellVariable(name = 'T', mesh = self.mesh)
		self.thermCond = FP.FaceVariable(name = 'lambda', mesh = self.mesh)
		# Create the coefficient for the source terms emulating boundary conditions
		self.cPrimCoeff = (self.primChannels * self.mesh.faceNormals).divergence
		self.cSecCoeff = (self.secChannels * self.mesh.faceNormals ).divergence
		self.cExtCoeff = (self.extChannel * self.mesh.faceNormals ).divergence

		# Initial guess
		self.T.setValue(heatExch.externalFlowIn.T)
		self.primChannelCalc.sections[0].fState.update_Tp(heatExch.primaryFlowIn.T, heatExch.primaryFlowIn.p)
		self.secChannelCalc.sections[0].fState.update_Tp(heatExch.secondaryFlowIn.T, heatExch.secondaryFlowIn.p)
		self.extChannelCalc.sections[0].fState.update_Tp(heatExch.externalFlowIn.T, heatExch.externalFlowIn.p)
		# Solve for a single cross section
		for i in range(self.numSectionSteps):
			heatExch.updateProgress((i + 1.0) / self.numSectionSteps, 1.)
			primSection = self.primChannelCalc.sections[i]
			secSection = self.secChannelCalc.sections[i]
			extSection = self.extChannelCalc.sections[i]
			# Compute convection coefficients
			primSection.computeConvectionCoefficient()
			secSection.computeConvectionCoefficient()
			extSection.computeConvectionCoefficient()
			# Run FV solver
			TPrim = primSection.fState.T 
			TSec = secSection.fState.T			
			TExt = extSection.fState.T
			self.solveSectionThermal(
				TPrim = TPrim, hConvPrim = primSection.hConv, 
				TSec = TSec, hConvSec = secSection.hConv, 
				TExt = TExt, hConvExt = extSection.hConv)
# 			self.checkResults(
# 				TPrim = TPrim, hConvPrim = primSection.hConv, 
# 				TSec = TSec, hConvSec = secSection.hConv, 
# 				TExt = TExt, hConvExt = extSection.hConv)			
			# Compute average channel wall temperatures
			TFaces = self.T.arithmeticFaceValue()
			TPrimWall = self.getFaceAverage(TFaces, self.primChannels)
			TSecWall = self.getFaceAverage(TFaces, self.secChannels)
			TExtWall = self.getFaceAverage(TFaces, self.extChannel)
			primSection.TWall = TPrimWall
			secSection.TWall = TSecWall
			extSection.TWall = TExtWall
			# Compute heat fluxes and new temperatures
			if (i < self.numSectionSteps - 1):
				primSection.computeExitState(self.primChannelCalc.sections[i + 1].fState)
				secSection.computeExitState(self.secChannelCalc.sections[i + 1].fState)
				extSection.computeExitState(self.extChannelCalc.sections[i + 1].fState)
			else:
				primSection.computeExitState(self.primChannelStateOut)
				secSection.computeExitState(self.secChannelStateOut)
				extSection.computeExitState(self.extChannelStateOut)
			# Make a section result plot
			if (i == 0 or (i - self.lastPlotPos) >= float(self.numSectionSteps) / self.numPlots or i == self.numSectionSteps - 1):
				if (self.currPlot <= self.numPlots):
					ax = heatExch.__getattr__('sectionPlot%d'%self.currPlot)
					ax.set_aspect('equal')
					ax.set_title('Section at x=%g' % primSection.xStart)
					if (heatExch.sectionResultsSettings.setTRange):
						self.plotSolution(heatExch, ax, self.T, 
							zmin = heatExch.sectionResultsSettings.Tmin,
							zmax = heatExch.sectionResultsSettings.Tmax)
					else:
						self.plotSolution(heatExch, ax, self.T)
					self.currPlot += 1
					self.lastPlotPos = i
			
			
	def plotSolution(self, heatExch, axes, var, zmin = None, zmax = None, cmap = cm.jet):
		vertexIDs = self.mesh._orderedCellVertexIDs
		vertexCoords = self.mesh.vertexCoords
		xCoords = np.take(vertexCoords[0], vertexIDs)
		yCoords = np.take(vertexCoords[1], vertexIDs)
		polys = []
		for x, y in zip(xCoords.swapaxes(0,1), yCoords.swapaxes(0,1)):
			if hasattr(x, 'mask'):
				x = x.compressed()
			if hasattr(y, 'mask'):
				y = y.compressed()
			polys.append(zip(x,y))
			
		from matplotlib.collections import PolyCollection
		# Set limits
		xmin = xCoords.min()
		xmax = xCoords.max()
		ymin = yCoords.min()
		ymax = yCoords.max()
		axes.set_xlim(xmin=xmin, xmax=xmax)
		axes.set_ylim(ymin=ymin, ymax=ymax)
		Z = var.value
		if (zmin is None):
			zmin = np.min(Z)
		if (zmax is None):
			zmax = np.max(Z)

		norm = Normalize(zmin, zmax)
		collection = PolyCollection(polys, cmap = cmap, norm = norm)
		collection.set_linewidth(0.)
		axes.add_collection(collection)

		cbax, _ = colorbar.make_axes(axes)
		cb = colorbar.ColorbarBase(cbax, cmap=cmap,
			norm = norm)
		cb.set_label('Temperature [K]')
 		collection.set_array(np.array(Z))
		
	def solveSectionThermal(self, TPrim, hConvPrim, TSec, hConvSec, TExt, hConvExt):				
		# Initialize convergence criteria
		res = 1e10
		n = 0
		# Run the non-linear iteration loop
		while (res > self.fvSolverSettings.tolerance and n < self.fvSolverSettings.maxNumIterations):
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
			res = eqT.sweep(var = self.T, solver = self.linSolver, underRelaxation = self.fvSolverSettings.relaxationFactor)
			#print n, res
			n += 1
	
	def checkResults(self, TPrim, hConvPrim, TSec, hConvSec, TExt, hConvExt):
		TFaces = self.T.arithmeticFaceValue()

		TPrimWall = self.getFaceAverage(TFaces, self.primChannels)
		TSecWall = self.getFaceAverage(TFaces, self.secChannels)
		TExtWall = self.getFaceAverage(TFaces, self.extChannel)
		
		QDotPrim = self.getFaceArea(self.primChannels) * hConvPrim * (TPrim - TPrimWall) 
		QDotSec = self.getFaceArea(self.secChannels) * hConvSec * (TSec - TSecWall) 
		QDotExt = self.getFaceArea(self.extChannel) * hConvExt * (TExt - TExtWall)
				
		Q1 = np.sum((hConvPrim * (self.T - TPrim) * self.cPrimCoeff * self.mesh.cellVolumes).value)
		Q2 = np.sum((hConvSec * (self.T - TSec) * self.cSecCoeff * self.mesh.cellVolumes).value)
		QExt = np.sum((hConvExt * (self.T - TExt) * self.cExtCoeff * self.mesh.cellVolumes).value)
		
		print QDotPrim, Q1
		print QDotSec, Q2
		print QDotExt, QExt
		print
	
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

