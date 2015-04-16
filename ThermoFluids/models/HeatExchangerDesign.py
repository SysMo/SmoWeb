'''
Created on Apr 8, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.model.model import NumericalModel
from smo.media.MaterialData import Fluids, Solids, IncompressibleSolutions
from heat_exchangers.HeatExchangerMesher import HeatExchangerMesher
from heat_exchangers.HeatExchangerSolver import HeatExchangerSolver
import smo.model.fields as F
import matplotlib.tri as tri
import numpy as np
import smo.media.CoolProp as CP

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
	
	def init(self):
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
	
	def init(self):
		self.cellSize = self.externalDiameter / (self.meshFineness * 2.5)
	
class MassFlow(NumericalModel):
	fluidName = F.Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
	mDot = F.Quantity('MassFlowRate', default = (0., 'kg/h'), 
		label = 'mass flow', description = 'mass flow rate of the channels')
	TIn = F.Quantity('Temperature', default = (0., 'K'), 
		label = 'inlet temperature', description = 'inlet temperature of the channels')
	pIn = F.Quantity('Pressure', default = (0., 'bar'), 
		label = 'inlet pressure', description = 'inlet pressure of the channels')
	FG = F.FieldGroup([fluidName, mDot, TIn, pIn], label = 'Parameters')
		
	modelBlocks = []
	
	def init(self):
		self.fluid = CP.Fluid(self.fluidName)
	
class VolumeFlow(NumericalModel):
	fluidName = F.Choices(IncompressibleSolutions, default = 'MEG', 
		label = 'fluid (name)', description = 'fluid (incompressible solutions)')
	fluidMassFraction = F.Quantity('Fraction', default = (0, '%'),
		label = 'fluid (mass fraction)', description = 'mass fraction of the substance other than water')
	vDot = F.Quantity('VolumetricFlowRate', default = (0., 'm**3/h'),
		label = 'volume flow', description = 'volume flow rate of the channels')
	TIn = F.Quantity('Temperature', default = (0., 'degC'), 
		label = 'inlet temperature', description = 'inlet temperature of the channels')
	pIn = F.Quantity('Pressure', default = (0., 'bar'), 
		label = 'inlet pressure', description = 'inlet pressure of the channels')
	
	FG = F.FieldGroup([fluidName, fluidMassFraction, vDot, TIn, pIn], label = 'Parameters')
	
	modelBlocks = []
	
	def init(self):
		#:TODO: (MILEN:TEST:DELME)
		#self.fState = CP5.FluidStateFactory.createIncompressibleSolution(self.fluidName, self.fluidMassFraction)
		#self.fState.update_Tp(self.TIn, self.pIn)
		#print "rho = ", self.fState.rho
		pass
		
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
	
	primaryChannelsGeom = F.SubModelGroup(ChannelGroupGeometry, 'FG', label  = 'Primary channels')
	secondaryChannelsGeom = F.SubModelGroup(ChannelGroupGeometry, 'FG', label  = 'Secondary channels')
	primaryFlow = F.SubModelGroup(MassFlow, 'FG', label = 'Primary flow')
	secondaryFlow = F.SubModelGroup(MassFlow, 'FG', label = 'Secondary flow')
	internalChannelSG = F.SuperGroup([primaryChannelsGeom, secondaryChannelsGeom, primaryFlow, secondaryFlow], label = 'Channels')
	
	# Fields: external channel
	externalChannelGeom = F.SubModelGroup(ExternalChannelGeometry, 'FG', label = 'Geometry')
	externalFlow = F.SubModelGroup(VolumeFlow, 'FG', label = 'Flow')
	externalChannelSG = F.SuperGroup([externalChannelGeom, externalFlow], label = 'External channel')
	
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [blockSG, internalChannelSG, externalChannelSG], 
						autoFetch = True)
	
	#================ Results ================#
	meshView = F.MPLPlot(label = 'Cross-section mesh')
	channelProfileView = F.MPLPlot(label = 'Channel profile')
	geometryVG = F.ViewGroup([meshView, channelProfileView], label = 'Geometry')
	resultsSG = F.SuperGroup([geometryVG], label = 'Geometry')
	
	resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])

	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	
	############# Methods ###############
	def __init__(self):
		self.blockGeom.diameter = (58.0, 'mm')
		self.blockGeom.length = (0.8, 'm')
		
		self.blockProps.material = 'Aluminium6061'
		self.blockProps.divisionStep = (0.02, 'm')
		
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
		
		self.primaryFlow.fluidName = 'ParaHydrogen'
		self.primaryFlow.mDot = (1, 'kg/h')
		self.primaryFlow.TIn = (100, 'K')
		self.primaryFlow.pIn = (1, 'bar') 
		
		self.secondaryFlow.fluidName = 'ParaHydrogen'
		self.secondaryFlow.mDot = (1, 'kg/h')
		self.secondaryFlow.TIn = (100, 'K')
		self.secondaryFlow.pIn = (1, 'bar') 
		
		self.externalFlow.fluidName = 'MEG'
		self.externalFlow.fluidMassFraction = (50, '%')
		self.externalFlow.vDot = (3, 'm**3/h')
		self.externalFlow.TIn = (80, 'degC')
		self.externalFlow.pIn = (1, 'bar') 
		
		self.externalChannelGeom.widthAxial = (30, 'mm')
		self.externalChannelGeom.heightRadial = (12, 'mm')
		self.externalChannelGeom.coilPitch = (32, 'mm')
		self.externalChannelGeom.averageCoilDiameter = (70, 'mm')
		self.externalChannelGeom.meshFineness = 4
	
	def preProcess(self):	
		# Initialize flows	
		self.primaryFlow.init()
		self.secondaryFlow.init()
		self.externalFlow.init()
		
		# Initialize geometries
		self.primaryChannelsGeom.init()
		self.secondaryChannelsGeom.init()
		self.externalChannelGeom.init()
		
	def preValidation(self):
		if self.blockGeom.diameter <= self.primaryChannelsGeom.externalDiameter:
			raise ValueError('The block diameter is less than the external diameter of the primary channels.')
		
		if self.blockGeom.diameter <= self.secondaryChannelsGeom.externalDiameter:
			raise ValueError('The block diameter is less than the external diameter of the secondary channels.')
		
		if self.blockGeom.diameter/2. <= (self.primaryChannelsGeom.radialPosition + self.primaryChannelsGeom.externalDiameter/2.):
			raise ValueError('The radial position of the primary channels is too big (the channels are outside of the block).')
		
		if self.blockGeom.diameter/2. <= (self.secondaryChannelsGeom.radialPosition + self.secondaryChannelsGeom.externalDiameter/2.):
			raise ValueError('The radial position of the secondary channels is too big (the channels are outside of the block).')
		
		
		
	def compute(self):
		self.preProcess()
		self.preValidation()
		
		# Create the mesh
		mesher = HeatExchangerMesher()
		mesher.create(self)
		
		# Create channel calculator objects
		solver = HeatExchangerSolver(mesher.mesh, 
				self.primaryChannelsGeom.number, 
				self.secondaryChannelsGeom.number)
		#solver.createChannelCalculators(self)
		
		self.postProcess(mesher, solver)
	
	def postProcess(self, mesher, solver):
		# Draw the mesh
		vertexCoords = mesher.mesh.vertexCoords
		vertexIDs = mesher.mesh._orderedCellVertexIDs
		triPlotMesh = tri.Triangulation(vertexCoords[0], vertexCoords[1], np.transpose(vertexIDs))
		self.meshView.triplot(triPlotMesh)
		self.meshView.set_aspect('equal')

		# Draw the channel Profile
# 		solver.primChannelCalc.plotGeometry(self.channelProfileView)
# 		self.channelProfileView.set_xlabel('[m]')
# 		self.channelProfileView.set_ylabel('[mm]')
# 		ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x*1e3))                                                                                                                                                                                                           
# 		self.channelProfileView.yaxis.set_major_formatter(ticks)  

		

