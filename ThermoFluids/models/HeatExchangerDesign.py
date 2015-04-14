'''
Created on Apr 8, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.model.actions import ServerAction, ActionBar
from smo.model.model import NumericalModel
from smo.media.MaterialData import Fluids
from smo.flow.HeatExchanger import HeatExchangerMesh
import smo.model.fields as F


class BlockGeometry(NumericalModel):
	diameter = F.Quantity('Length', default = (100, 'mm'),
		label = 'diameter', description = 'block diameter')
	cellSize = F.Quantity('Length', default = (5, 'mm'), 
		label = 'mesh cell size', description = 'mesh cell size near the outer block circle')
	
	FG = F.FieldGroup([diameter, cellSize], label = 'Block geometry')
	
	modelBlocks = []
	
class ChannelGeometry(NumericalModel):
	externalDiameter = F.Quantity('Length', default = (7.5, 'mm'),
		label = 'external diameter', description = 'external diameter of the channels')
	
	sections = F.RecordArray((
			('internalDiameter', F.Quantity('Length', default = (0, 'mm'), label = 'internal diameter')),
			('length', F.Quantity('Length', default = (0.2, 'm'), label = 'length')),		
			('numDivisions', F.Quantity('Dimensionless', default = (5, '-'), label = 'number divisions')),
		), 
		label = 'sections',
		numRows = 5)
	
	FG = F.FieldGroup([externalDiameter, sections], label = 'Channel geometry')
	
	modelBlocks = []
	
class ChannelGroup(NumericalModel):
	number = F.Quantity('Dimensionless', default = (3, '-'), minValue = (0, '-'),
		label = 'number', description = 'number of channels')
	radialPosition = F.Quantity('Length', default = (30, 'mm'), minValue = (0, 'mm'), 
		label = 'radial position', description = 'radial position of the channels')
	startingAngle = F.Quantity('Angle', default = (0, 'deg'), minValue = (-1e6, 'deg'),
		label = 'starting angle', description = 'starting angle of the first')
	cellSize = F.Quantity('Length', default = (1, 'mm'), 
		label = 'mesh cell size', description = 'mesh cell size near the channels')
	
	channelGeom =  F.SubModelGroup(ChannelGeometry, 'FG', 'Channel geometry')
	channelName = F.String()
	
	FG = F.FieldGroup([number, radialPosition, startingAngle, cellSize], 
        label = 'Parameters')
	
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
	# Field group: Block geometry	
	blockGeom = F.SubModelGroup(BlockGeometry, 'FG', 'Block geometry')
	channelGeom = F.SubModelGroup(ChannelGeometry, 'FG', 'Channel geometry') 
	primaryChannels = F.SubModelGroup(ChannelGroup, 'FG', label  = 'Primary channels')
	secondaryChannels = F.SubModelGroup(ChannelGroup, 'FG', label  = 'Secondary channels')

	inputValues = F.SuperGroup([blockGeom, channelGeom, primaryChannels, secondaryChannels], label = 'Input values')
	
	# Field group: Flow
	#:TODO: (MILEN: DELME)
	fluidPrim = F.Choices(Fluids, default = 'ParaHydrogen', label = 'fluid primary')
	mDotPrim = F.Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mDot primary',
				description = 'mass flow rate of the primary channel')
	TInPrim = F.Quantity('Temperature', default = (100, 'K'), label = 'T inlet primary', 
				description = 'inlet temperature of the primary channel')
	pInPrim = F.Quantity('Pressure', default = (1, 'bar'), label = 'p inlet primary', 
				description = 'inlet pressure of the primary channel')

	fluidSec = F.Choices(Fluids, default = 'ParaHydrogen', label = 'fluid secondary')
	mDotSec = F.Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mDot secondary',
				description = 'mass flow rate of the secondary channel')
	TInSec = F.Quantity('Temperature', default = (100, 'K'), label = 'T inlet secondary', 
				description = 'inlet temperature of the secondary channel')
	pInSec = F.Quantity('Pressure', default = (1, 'bar'), label = 'p inlet secondary', 
				description = 'inlet pressure of the secondary channel')

	mDotExt = F.Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mDot external',
				description = 'mass flow rate of the external channel')
	TInExt = F.Quantity('Temperature', default = (100, 'K'), label = 'T inlet external', 
				description = 'inlet temperature of the external channel')
	pInExt = F.Quantity('Pressure', default = (1, 'bar'), label = 'p inlet external', 
				description = 'inlet pressure of the external channel')

	flowGroup = F.FieldGroup([fluidPrim, mDotPrim, TInPrim, pInPrim, fluidSec, mDotSec, TInSec, pInSec, 
							mDotExt, TInExt, pInExt], label = 'Fluid flows')
	
	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputValues], 
		actionBar = inputActionBar, autoFetch = True)
	
	#================ Results ================#
	meshImage = F.Image(default='')
	meshImageVG = F.ViewGroup([meshImage], label = 'Heat exchanger cross section')
	resultsSG = F.SuperGroup([meshImageVG], label = 'Mesh')
	
	resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])

	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	
	############# Methods ###############
	def __init__(self):
		self.blockGeom.diameter = (58.0, 'mm')
		self.blockGeom.cellSize = (2.0, 'mm')
		
		self.channelGeom.externalDiameter = (7.5, 'mm')
		self.channelGeom.sections[0] = (0.002, 0.2, 5)
		self.channelGeom.sections[1] = (0.004, 0.1, 5)
		self.channelGeom.sections[2] = (0.006, 0.1, 5)
		self.channelGeom.sections[3] = (0.0065, 0.1, 5)
		self.channelGeom.sections[4] = (0.007, 0.3, 5)
		
		self.primaryChannels.number = (3, '-')
		self.primaryChannels.radialPosition = (7, 'mm')
		self.primaryChannels.startingAngle = (0, 'deg')
		self.primaryChannels.cellSize = (1, 'mm')
		self.primaryChannels.channelName = "PrimaryChannel"
		
		self.secondaryChannels.number = (3, '-')
		self.secondaryChannels.radialPosition = (17.5, 'mm')
		self.secondaryChannels.startingAngle = (60, 'deg')
		self.secondaryChannels.cellSize = (1, 'mm')
		self.primaryChannels.channelName = "SecondaryChannel"
		
	def compute(self):
		# Initialize
		self.primaryChannels.channelGeom = self.channelGeom
		self.secondaryChannels.channelGeom = self.channelGeom
		
		# Create the mesh
		mesh = HeatExchangerMesh()
		mesh.create(self)
		
		# Show the mesh
		tmpFilePath  = mesh.plotToTmpFile()
		self.meshImage = tmpFilePath