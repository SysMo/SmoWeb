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
	blockDiameter = F.Quantity('Length', default = (100, 'mm'), label = 'block diameter')
	blockCellSize = F.Quantity('Length', default = (5, 'mm'), label = 'block cell size (mesh)')
	primaryChannels = F.RecordArray((
			('diameter', F.Quantity('Length', default = (10, 'mm'), label = 'channel diameter')),
			('r', F.Quantity('Length', default = (30, 'mm'), label = 'radial position')),		
			('theta', F.Quantity('Angle', default = (0, 'deg'), label = 'angular position', minValue = (-1e6, 'deg'))),
			('cellSize', F.Quantity('Length', default = (1, 'mm'), label = 'cell size (mesh)')),
		), 
		label = 'primary channels',
		empty = True,
		numRows = 3,)
	
	secondaryChannels = F.RecordArray((
			('diameter', F.Quantity('Length', default = (10, 'mm'), label = 'channel diameter')),
			('r', F.Quantity('Length', default = (15, 'mm'), label = 'radial position')),		
			('theta', F.Quantity('Angle', default = (0, 'deg'), label = 'angular position', minValue = (-1e6, 'deg'))),
			('cellSize', F.Quantity('Length', default = (1, 'mm'), label = 'cell size (mesh)')),
		), 
		label = 'secondary channels',
		empty = True,
		numRows = 3,)
	
	blockGeometryGroup = F.FieldGroup([blockDiameter, blockCellSize, primaryChannels, secondaryChannels], label = 'Block geometry')

	# Field group: Flow
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
	inputValues = F.SuperGroup([blockGeometryGroup, flowGroup], label = 'Input values')
	#inputValues = F.SuperGroup([blockGeometryGroup], label = 'Input values') #:TEST:
	
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
		self.blockDiameter = (58.0, 'mm')
		self.blockCellSize = (2.0, 'mm')
		
		d = (7.5, 'mm')
		cellSize = (1, 'mm')
		rPrimary = (7, 'mm')
		rSecondar = (17.5, 'mm')
		
		#self.primaryChannels[0] = 
		
	def compute(self):		
		# Create the mesh
		mesh = HeatExchangerMesh()
		mesh.create(self)
		
		# Show the mesh
		tmpFilePath  = mesh.plotToTmpFile()
		self.meshImage = tmpFilePath
	