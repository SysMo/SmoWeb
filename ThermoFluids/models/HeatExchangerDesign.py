'''
Created on Apr 8, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.model.model import NumericalModel
from smo.media.MaterialData import Fluids
from heat_exchangers.HeatExchangerMesher import HeatExchangerMesher
from heat_exchangers.HeatExchangerSolver import HeatExchangerSolver
import smo.model.fields as F
import matplotlib.tri as tri
import numpy as np
import smo.media.CoolProp as CP

class BlockGeometry(NumericalModel):
	diameter = F.Quantity('Length', default = (0., 'mm'),
		label = 'diameter', description = 'block diameter')
	
	length = F.Quantity('Length', default = (0., 'm'),
		label = 'length', description = 'block length')
	
	divisionStep = F.Quantity('Length', default = (0., 'm'),
		label = 'division step', description = 'axial division step')
	
	FG = F.FieldGroup([diameter, length, divisionStep], label = 'Block geometry')
	
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
	
	FG = F.FieldGroup([widthAxial, heightRadial, coilPitch, averageCoilDiameter, cellSize], 
		label = 'Channel geometry')
		
	modelBlocks = []
	
class ChannelGroupGeometry(NumericalModel):
	number = F.Integer(default = 0, minValue = 0,
		label = 'number', description = 'number of channels')
	radialPosition = F.Quantity('Length', default = (0., 'mm'), minValue = (0, 'mm'), 
		label = 'radial position', description = 'radial position of the channels')
	startingAngle = F.Quantity('Angle', default = (0., 'deg'), minValue = (-1e6, 'deg'),
		label = 'starting angle', description = 'starting angle of the first')
	cellSize = F.Quantity('Length', default = (0., 'mm'), 
		label = 'mesh cell size', description = 'mesh cell size near the channels')
	
	externalDiameter = F.Quantity('Length', default = (0., 'mm'),
		label = 'external diameter', description = 'external diameter of the channels')
	sections = F.RecordArray((
			('internalDiameter', F.Quantity('Length', default = (0, 'mm'), label = 'internal diameter')),
			('length', F.Quantity('Length', default = (0.2, 'm'), label = 'length')),		
			('numDivisions', F.Integer(default = 5, label = 'number divisions')),
		), 
		label = 'sections',
		numRows = 5)
	
	channelName = F.String()
	
	FG = F.FieldGroup([number, radialPosition, startingAngle, externalDiameter, sections, cellSize], label = 'Parameters')
	
	modelBlocks = []
	
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
	fluidName = F.Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
	vDot = F.Quantity('VolumetricFlowRate', default = (0., 'm**3/h'),
		label = 'volume flow', description = 'volume flow rate of the channels')
	TIn = F.Quantity('Temperature', default = (0., 'degC'), 
		label = 'inlet temperature', description = 'inlet temperature of the channels')
	pIn = F.Quantity('Pressure', default = (0., 'bar'), 
		label = 'inlet pressure', description = 'inlet pressure of the channels')
	
	FG = F.FieldGroup([fluidName, vDot, TIn, pIn], label = 'Parameters')
	
	modelBlocks = []
	
	def init(self):
		self.fluid = CP.Fluid(self.fluidName)
		
		self.fState = CP.FluidState(self.fluid)
		self.fState.update_Tp(self.TIn, self.pIn)
		self.mDot = self.vDot * self.fState.rho
		
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
	blockSG = F.SuperGroup([blockGeom], label = 'Block')
	
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
		self.blockGeom.divisionStep = (0.02, 'm')
		
		self.primaryChannelsGeom.number = 3
		self.primaryChannelsGeom.radialPosition = (7, 'mm')
		self.primaryChannelsGeom.startingAngle = (0, 'deg')
		self.primaryChannelsGeom.cellSize = (1, 'mm')
		self.primaryChannelsGeom.channelName = "PrimaryChannel"
		
		self.primaryChannelsGeom.externalDiameter = (7.5, 'mm')
		self.primaryChannelsGeom.sections[0] = (0.002, 0.2, 5)
		self.primaryChannelsGeom.sections[1] = (0.004, 0.1, 5)
		self.primaryChannelsGeom.sections[2] = (0.006, 0.1, 5)
		self.primaryChannelsGeom.sections[3] = (0.0065, 0.1, 5)
		self.primaryChannelsGeom.sections[4] = (0.007, 0.3, 5)
		
		self.secondaryChannelsGeom.number = 3
		self.secondaryChannelsGeom.radialPosition = (17.5, 'mm')
		self.secondaryChannelsGeom.startingAngle = (60, 'deg')
		self.secondaryChannelsGeom.cellSize = (1, 'mm')
		self.secondaryChannelsGeom.channelName = "SecondaryChannel"
		
		self.secondaryChannelsGeom.externalDiameter = (7.5, 'mm')
		self.secondaryChannelsGeom.sections[0] = (0.002, 0.2, 5)
		self.secondaryChannelsGeom.sections[1] = (0.004, 0.1, 5)
		self.secondaryChannelsGeom.sections[2] = (0.006, 0.1, 5)
		self.secondaryChannelsGeom.sections[3] = (0.0065, 0.1, 5)
		self.secondaryChannelsGeom.sections[4] = (0.007, 0.3, 5)
		
		self.primaryFlow.fluidName = 'ParaHydrogen'
		self.primaryFlow.mDot = (1, 'kg/h')
		self.primaryFlow.TIn = (100, 'K')
		self.primaryFlow.pIn = (1, 'bar') 
		
		self.secondaryFlow.fluidName = 'ParaHydrogen'
		self.secondaryFlow.mDot = (1, 'kg/h')
		self.secondaryFlow.TIn = (100, 'K')
		self.secondaryFlow.pIn = (1, 'bar') 
		
		self.externalFlow.fluidName = 'Water'
		self.externalFlow.vDot = (3, 'm**3/h')
		self.externalFlow.TIn = (80, 'degC')
		self.externalFlow.pIn = (1, 'bar') 
		
		self.externalChannelGeom.widthAxial = (30, 'mm')
		self.externalChannelGeom.heightRadial = (12, 'mm')
		self.externalChannelGeom.coilPitch = (32, 'mm')
		self.externalChannelGeom.averageCoilDiameter = (70, 'mm')
		self.externalChannelGeom.cellSize = (2.0, 'mm')
		
	def compute(self):
		# Initialize		
		self.primaryFlow.init()
		self.secondaryFlow.init()
		self.externalFlow.init()
		
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

		
