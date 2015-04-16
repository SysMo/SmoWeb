'''
Created on Apr 8, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.model.model import NumericalModel
from smo.media.MaterialData import Fluids, Solids, IncompressibleSolutions
from heat_exchangers.HeatExchangerMesher import HeatExchangerMesher
from heat_exchangers.HeatExchangerSolver import HeatExchangerSolver
from heat_exchangers.HeatExchangerCrossSectionProfile import HeatExchangerCrossSectionProfile
import smo.model.fields as F
import matplotlib.tri as tri
import matplotlib.ticker as ticker
import numpy as np
from collections import OrderedDict
import smo.media.CoolProp as CP
import smo.media.CoolProp5 as CP5

class BlockProperties(NumericalModel):
	material = F.ObjectReference(Solids, default = 'Aluminium6061', 
		label = 'material', description = 'block material')
	divisionStep = F.Quantity('Length', default = (0., 'm'), #:TODO: (MILEN:WORK) Add Validation
		label = 'division step (axial)', description = 'axial division step')
	
	FG = F.FieldGroup([material, divisionStep], label = 'Block properties')
	
	modelBlocks = []

class BlockGeometry(NumericalModel):
	diameter = F.Quantity('Length', default = (0., 'mm'),
		label = 'diameter', description = 'block diameter')
	length = F.Quantity('Length', default = (0., 'm'), #:TODO: (MILEN:WORK) Add Validation
		label = 'length', description = 'block length')
	
	FG = F.FieldGroup([diameter, length], label = 'Block geometry')
	
	modelBlocks = []
	
class ExternalChannelGeometry(NumericalModel):
	widthAxial = F.Quantity('Length', default = (0., 'mm'),
		label = 'width (axial)', description = 'axial width of the spiral rectangular channel')
	heightRadial = F.Quantity('Length', default = (0., 'mm'),
		label = 'radial height', description = 'radial height of the spiral rectangular channel')
	coilPitch = F.Quantity('Length', default = (0., 'mm'),
		label = 'coil pitch', description = 'coil pitch of the spiral rectangular channel')
	averageCoilDiameter = F.Quantity('Length', default = (0., 'mm'),
		label = 'average coil diameter', description = 'average coil diameter of the spiral rectangular channel')
	
	cellSize = F.Quantity('Length', default = (0., 'mm'), 
		label = 'mesh cell size', description = 'mesh cell size near the outer block circle')
	meshFineness = F.Integer(default = 1, minValue = 1, maxValue = 10,
		label = 'mesh fineness', description = 'mesh fineness near the outer side of the block')
		
	FG = F.FieldGroup([widthAxial, heightRadial, coilPitch, averageCoilDiameter, meshFineness], 
		label = 'Channel geometry')
		
	modelBlocks = []
	
	def compute(self):
		self.cellSize = self.averageCoilDiameter / (self.meshFineness * 10.)
	
class ChannelGroupGeometry(NumericalModel):
	number = F.Integer(default = 0, minValue = 0, maxValue = 30,
		label = 'number', description = 'number of channels')
	radialPosition = F.Quantity('Length', default = (0., 'mm'), minValue = (0, 'mm'), 
		label = 'radial position', description = 'radial position of the channels')
	startingAngle = F.Quantity('Angle', default = (0., 'deg'), minValue = (-1e6, 'deg'),
		label = 'starting angle', description = 'starting angle of the first')
	
	cellSize = F.Quantity('Length', default = (0., 'mm'), 
		label = 'mesh cell size', description = 'mesh cell size near the channels')
	meshFineness = F.Integer(default = 1, minValue = 1, maxValue = 10,
		label = 'mesh fineness', description = 'mesh fineness near the channels')
	
	externalDiameter = F.Quantity('Length', default = (0., 'mm'),
		label = 'external diameter', description = 'external diameter of the channels')
	sections = F.RecordArray((
			('internalDiameter', F.Quantity('Length', default = (0, 'mm'), label = 'internal diameter')),
			('length', F.Quantity('Length', default = (0.2, 'm'), label = 'length')),
		), 
		label = 'sections',
		numRows = 5)
	
	channelName = F.String()
	
	FG = F.FieldGroup([number, radialPosition, startingAngle, externalDiameter, sections, meshFineness], label = 'Parameters')
	
	modelBlocks = []
	
	def compute(self):
		self.cellSize = self.externalDiameter / (self.meshFineness * 2.5)
	
class FluidFlowInput(NumericalModel):
	fluidName = F.Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
	flowRateChoice = F.Choices(OrderedDict((
		('V', 'volume'),
		('m', 'mass'),
	)), label = 'flow rate based on')
	mDot = F.Quantity('MassFlowRate', minValue = (0, 'kg/h'), default = (1., 'kg/h'), 
		label = 'mass flow', description = 'mass flow rate', show = 'self.flowRateChoice == "m"')
	VDot = F.Quantity('VolumetricFlowRate', minValue = (0., 'm**3/h'), default = (1., 'm**3/h'),
		label = 'volume flow', description = 'volume flow rate', show = 'self.flowRateChoice == "V"')
	T = F.Quantity('Temperature', default = (300., 'K'), label = 'temperature')
	p = F.Quantity('Pressure', default = (1., 'bar'), label = 'pressure')
	FG = F.FieldGroup([fluidName, flowRateChoice, mDot, VDot, T, p], label = 'Parameters')
		
	modelBlocks = []
	
	def createFluidState(self):
		return CP.FluidState(self.fluidName)
	
	def compute(self):
		fState = self.createFluidState()
		fState.update_Tp(self.T, self.p)
		if (self.flowRateChoice == 'm'):
			self.VDot = self.mDot / fState.rho
		else:
			self.mDot = self.VDot * fState.rho
			
class IncompressibleSolutionFlowInput(FluidFlowInput):
	solName = F.Choices(IncompressibleSolutions, default = 'MEG', 
		label = 'fluid (name)', description = 'fluid (incompressible solutions)')
	solMassFraction = F.Quantity('Fraction', default = (0, '%'),
		label = 'fluid (mass fraction)', description = 'mass fraction of the substance other than water')
	
	incomSolFG = F.FieldGroup([solName, solMassFraction, 'flowRateChoice', 'mDot', 'VDot', 'T', 'p'], label = 'Parameters')
	
	def createFluidState(self):
		return CP5.FluidStateFactory.createIncompressibleSolution(self.solName, self.solMassFraction)
		
class FluidFlowOutput(NumericalModel):
	VDot = F.Quantity('VolumetricFlowRate', minValue = (0., 'm**3/h'), default = (1., 'm**3/h'),
		label = 'volume flow', description = 'volume flow rate')
	mDot = F.Quantity('MassFlowRate', minValue = (0, 'kg/h'), default = (1., 'kg/h'), 
		label = 'mass flow', description = 'mass flow rate')
	T = F.Quantity('Temperature', default = (300., 'K'), label = 'temperature')
	p = F.Quantity('Pressure', default = (1., 'bar'),  label = 'pressure')
	FG = F.FieldGroup([mDot, VDot, T, p], label = 'Parameters')
		
	modelBlocks = []
	
	def compute(self, fState, mDot):
		self.T = fState.T
		self.p = fState.p
		self.mDot = mDot
		self.VDot = mDot / fState.rho


class FiniteVolumeSolverSettings(NumericalModel):
	tolerance = F.Quantity(default = 1e-6, label = 'tolerance')
	maxNumIterations = F.Integer(default = 100, label = 'max number iterations')
	relaxationFactor = F.Quantity(default = 1.0, label = 'relaxation factor')
	
	FG = F.FieldGroup([tolerance, maxNumIterations, relaxationFactor], label = 'Settings')

	modelBlocks = []
	
class CylindricalBlockHeatExchanger(NumericalModel):
	label = "Cylindrical heat exchanger"
	#figure = F.ModelFigure()
	description = F.ModelDescription(
	"""Model of heat exchanger made out of a solid cylindrical block, with
	central channels for one of the fluids and a spiraling
	channel around the block for the other fluid
	""")

	#================ Inputs ================#
	#---------------- Fields ----------------#
	# Fields: geometry	
	blockGeom = F.SubModelGroup(BlockGeometry, 'FG', 'Geometry')
	blockProps = F.SubModelGroup(BlockProperties, 'FG', 'Properties')
	blockSG = F.SuperGroup([blockGeom, blockProps], label = 'Block')
	
	# Fields: internal channels
	primaryChannelsGeom = F.SubModelGroup(ChannelGroupGeometry, 'FG', label  = 'Primary channels')
	secondaryChannelsGeom = F.SubModelGroup(ChannelGroupGeometry, 'FG', label  = 'Secondary channels')
	primaryFlowIn = F.SubModelGroup(FluidFlowInput, 'FG', label = 'Primary flow inlet')
	secondaryFlowIn = F.SubModelGroup(FluidFlowInput, 'FG', label = 'Secondary flow inlet')
	internalChannelSG = F.SuperGroup([primaryChannelsGeom, secondaryChannelsGeom, primaryFlowIn, secondaryFlowIn], label = 'Channels')
	
	# Fields: external channel
	externalChannelGeom = F.SubModelGroup(ExternalChannelGeometry, 'FG', label = 'Geometry')
	externalFlowIn = F.SubModelGroup(IncompressibleSolutionFlowInput, 'incomSolFG', label = 'Inlet flow')
	externalChannelSG = F.SuperGroup([externalChannelGeom, externalFlowIn], label = 'External channel')
	
	# Fields: thermal solver settings
	fvSolverSettings = F.SubModelGroup(FiniteVolumeSolverSettings, 'FG', label = 'Finite volume solver') 
	solverSettingsSG = F.SuperGroup([fvSolverSettings], label = 'Solver settings')
	
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [blockSG, internalChannelSG, externalChannelSG, solverSettingsSG], 
						autoFetch = True)
	
	#================ Results ================#
	meshView = F.MPLPlot(label = 'Cross-section mesh')
	crossSectionProfileView = F.MPLPlot(label = 'Cross-section profile')
	primaryChannelProfileView = F.MPLPlot(label = 'Primary channel profile')
	secondaryChannelProfileView = F.MPLPlot(label = 'Secondary channel profile')
	geometryVG = F.ViewGroup([meshView, crossSectionProfileView, primaryChannelProfileView, secondaryChannelProfileView], label = 'Geometry/Mesh')
	geometrySG = F.SuperGroup([geometryVG], label = 'Geometry/mesh')
	
	primaryFlowOut = F.SubModelGroup(FluidFlowOutput, 'FG', label = 'Primary flow outlet')
	secondaryFlowOut = F.SubModelGroup(FluidFlowOutput, 'FG', label = 'Secondary flow outlet')
	externalFlowOut = F.SubModelGroup(FluidFlowOutput, 'FG', label = 'External flow outlet')
	resultSG = F.SuperGroup([primaryFlowOut, secondaryFlowOut, externalFlowOut], label = 'Results')
	
	resultTable = F.TableView((
		('xStart', F.Quantity('Length', default = (1, 'm'))),
		('xEnd', F.Quantity('Length', default = (1, 'm'))),		
		('TPrimFluid', F.Quantity('Temperature', default = (1, 'degC'))),
		('TPrimWall', F.Quantity('Temperature', default = (1, 'degC'))),
		('RePrim', F.Quantity()),
		('hConvPrim', F.Quantity('HeatTransferCoefficient', default = (1, 'W/m**2-K'))),
		('TSecFluid', F.Quantity('Temperature', default = (1, 'degC'))),
		('TSecWall', F.Quantity('Temperature', default = (1, 'degC'))),
		('hConvSec', F.Quantity('HeatTransferCoefficient', default = (1, 'W/m**2-K'))),
		('ReSec', F.Quantity()),
	), label = 'Detailed results')
	resultTPlot = F.PlotView((
		('x', F.Quantity('Length', default = (1, 'm'))),
		('TPrimFluid', F.Quantity('Temperature', default = (1, 'degC'))),
		('TPrimWall', F.Quantity('Temperature', default = (1, 'degC'))),
		('TSecFluid', F.Quantity('Temperature', default = (1, 'degC'))),
		('TSecWall', F.Quantity('Temperature', default = (1, 'degC'))),
	), label = 'Temperature plots')
	
	detailedResultVG = F.ViewGroup([resultTable, resultTPlot], label = 'Detailed results')
	detailedResultSG = F.SuperGroup([detailedResultVG], label = 'Detailed results')
	
	sectionPlot1 = F.MPLPlot(label = 'Section 1')
	sectionPlot2 = F.MPLPlot(label = 'Section 2')
	sectionPlot3 = F.MPLPlot(label = 'Section 3')
	sectionPlot4 = F.MPLPlot(label = 'Section 4')
	sectionPlot5 = F.MPLPlot(label = 'Section 5')
	sectionResultsVG = F.ViewGroup([sectionPlot1, sectionPlot2, sectionPlot3, sectionPlot4, sectionPlot5],
		label = 'Section temperatures')
	sectionResultsSG = F.SuperGroup([sectionResultsVG], label = 'Section results')
	
	resultView = F.ModelView(ioType = "output", superGroups = [geometrySG, resultSG, detailedResultSG, sectionResultsSG])

	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	
	############# Methods ###############
	def __init__(self):
		self.blockGeom.diameter = (58.0, 'mm')
		self.blockGeom.length = (0.8, 'm')
		self.blockProps.divisionStep = (0.1, 'm')
		self.blockProps.material = 'Aluminium6061'
		
		self.primaryChannelsGeom.number = 3
		self.primaryChannelsGeom.radialPosition = (7, 'mm')
		self.primaryChannelsGeom.startingAngle = (0, 'deg')
		self.primaryChannelsGeom.meshFineness = 4
		self.primaryChannelsGeom.channelName = "PrimaryChannel"
		
		self.primaryChannelsGeom.externalDiameter = (7.5, 'mm')
		self.primaryChannelsGeom.sections[0] = (0.002, 0.2)
		self.primaryChannelsGeom.sections[1] = (0.004, 0.1)
		self.primaryChannelsGeom.sections[2] = (0.006, 0.1)
		self.primaryChannelsGeom.sections[3] = (0.0065, 0.1)
		self.primaryChannelsGeom.sections[4] = (0.007, 0.3)
		
		self.secondaryChannelsGeom.number = 3
		self.secondaryChannelsGeom.radialPosition = (17.5, 'mm')
		self.secondaryChannelsGeom.startingAngle = (60, 'deg')
		self.secondaryChannelsGeom.meshFineness = 4
		self.secondaryChannelsGeom.channelName = "SecondaryChannel"
		
		self.secondaryChannelsGeom.externalDiameter = (7.5, 'mm')
		self.secondaryChannelsGeom.sections[0] = (0.002, 0.2)
		self.secondaryChannelsGeom.sections[1] = (0.004, 0.1)
		self.secondaryChannelsGeom.sections[2] = (0.006, 0.1)
		self.secondaryChannelsGeom.sections[3] = (0.0065, 0.1)
		self.secondaryChannelsGeom.sections[4] = (0.007, 0.3)
		
		self.primaryFlowIn.fluidName = 'ParaHydrogen'
		self.primaryFlowIn.flowRateChoice = 'm'
		self.primaryFlowIn.mDot = (1, 'kg/h')
		self.primaryFlowIn.T = (100, 'K')
		self.primaryFlowIn.p = (1, 'bar') 
		
		self.secondaryFlowIn.fluidName = 'ParaHydrogen'
		self.secondaryFlowIn.flowRateChoice = 'm'
		self.secondaryFlowIn.mDot = (1, 'kg/h')
		self.secondaryFlowIn.T = (100, 'K')
		self.secondaryFlowIn.p = (1, 'bar') 
		
		self.externalFlowIn.solName = 'MEG'
		self.externalFlowIn.solMassFraction = (50, '%')
		self.externalFlowIn.flowRateChoice = 'V'
		self.externalFlowIn.vDot = (3, 'm**3/h')
		self.externalFlowIn.T = (80, 'degC')
		self.externalFlowIn.p = (1, 'bar') 
		
		self.externalChannelGeom.widthAxial = (30, 'mm')
		self.externalChannelGeom.heightRadial = (12, 'mm')
		self.externalChannelGeom.coilPitch = (32, 'mm')
		self.externalChannelGeom.averageCoilDiameter = (70, 'mm')
		self.externalChannelGeom.meshFineness = 4		
		
	def compute(self):
		# Validation
		self.validateInputs()
		
		# PreComputation
		self.externalChannelGeom.compute()
		self.primaryChannelsGeom.compute()
		self.secondaryChannelsGeom.compute()
		
		self.primaryFlowIn.compute()
		self.secondaryFlowIn.compute()
		self.externalFlowIn.compute()
		
		# Create the mesh
		mesher = HeatExchangerMesher()
		mesher.create(self)
		
		# Create channel calculator objects
		solver = HeatExchangerSolver(self, mesher)
		solver.createChannelCalculators(self)
		solver.solve(self)
		
		# Produce geometry/mesh drawings
		self.drawGeometry(mesher, solver)
		
		# Produce results		
		self.postProcess(mesher, solver)
		
	def validateInputs(self):
		if self.blockGeom.diameter <= self.primaryChannelsGeom.externalDiameter:
			raise ValueError('The block diameter is less than the external diameter of the primary channels.')
		
		if self.blockGeom.diameter <= self.secondaryChannelsGeom.externalDiameter:
			raise ValueError('The block diameter is less than the external diameter of the secondary channels.')
		
		if self.blockGeom.diameter/2. <= (self.primaryChannelsGeom.radialPosition + self.primaryChannelsGeom.externalDiameter/2.):
			raise ValueError('The radial position of the primary channels is too big (the channels are outside of the block).')
		
		if self.blockGeom.diameter/2. <= (self.secondaryChannelsGeom.radialPosition + self.secondaryChannelsGeom.externalDiameter/2.):
			raise ValueError('The radial position of the secondary channels is too big (the channels are outside of the block).')
		
	
	def drawGeometry(self, mesher, solver):
		# Draw the mesh
		vertexCoords = mesher.mesh.vertexCoords
		vertexIDs = mesher.mesh._orderedCellVertexIDs
		triPlotMesh = tri.Triangulation(vertexCoords[0], vertexCoords[1], np.transpose(vertexIDs))
		self.meshView.triplot(triPlotMesh)
		self.meshView.set_aspect('equal')
		
		#Draw heat exchanger cross-section profile
		crossSectionProfile = HeatExchangerCrossSectionProfile()
		crossSectionProfile.addBlock(self.blockGeom)
		crossSectionProfile.addChannels(self.primaryChannelsGeom)
		crossSectionProfile.addChannels(self.secondaryChannelsGeom)
		crossSectionProfile.plotGeometry(self.crossSectionProfileView)

		# Draw the channels profiles
		ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x*1e3))                                                                                                                                                                                                           

		solver.primChannelCalc.plotGeometry(self.primaryChannelProfileView)
		self.primaryChannelProfileView.set_xlabel('[m]')
		self.primaryChannelProfileView.set_ylabel('[mm]')
		self.primaryChannelProfileView.yaxis.set_major_formatter(ticks)  

		solver.secChannelCalc.plotGeometry(self.secondaryChannelProfileView)
		self.secondaryChannelProfileView.set_xlabel('[m]')
		self.secondaryChannelProfileView.set_ylabel('[mm]')
		self.secondaryChannelProfileView.yaxis.set_major_formatter(ticks)  
		
	def postProcess(self, mesher, solver):
		# Get the value for the outlet conditions
		self.primaryFlowOut.compute(fState = solver.primChannelStateOut, mDot = self.primaryFlowIn.mDot) 
		self.secondaryFlowOut.compute(fState = solver.secChannelStateOut, mDot = self.secondaryFlowIn.mDot)
		#self.externalFlowOut.compute(fState = ..., mDot = self.externalFlowIn.mDot)
		# Fill the table with values
		self.resultTable.resize(solver.numSectionSteps)
		self.resultTPlot.resize(solver.numSectionSteps)
		for i in range(solver.numSectionSteps):
			self.resultTable[i] = (
				solver.primChannelCalc.sections[i].xStart,
				solver.primChannelCalc.sections[i].xEnd,
				solver.primChannelCalc.sections[i].fState.T,
				solver.primChannelCalc.sections[i].TWall,
				solver.primChannelCalc.sections[i].Re,
				solver.primChannelCalc.sections[i].hConv,
				solver.secChannelCalc.sections[i].fState.T,
				solver.secChannelCalc.sections[i].TWall,
				solver.secChannelCalc.sections[i].hConv,
				solver.secChannelCalc.sections[i].Re,
			)
			self.resultTPlot[i] = (
				(solver.primChannelCalc.sections[i].xStart + 
				solver.primChannelCalc.sections[i].xEnd) / 2,
				solver.primChannelCalc.sections[i].fState.T,
				solver.primChannelCalc.sections[i].TWall,
				solver.secChannelCalc.sections[i].fState.T,
				solver.secChannelCalc.sections[i].TWall,
			)