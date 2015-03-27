'''
Created on Mar 27, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.model.actions import ServerAction, ActionBar
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from lib.CycleBases import LiquefierCycle
import smo.web.exceptions as E

class LindeHampsonCycle(LiquefierCycle):
	label = "Linde-Hampson cycle"
	figure = F.ModelFigure(src="ThermoFluids/img/ModuleImages/RankineCycle.png",  height = 300)
	description = F.ModelDescription("Basic liquefaction cycle used e.g. for air liquefaction", show = True)

	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	compressor = F.SubModelGroup(TC.Compressor, 'FG', label  = 'Compressor')
	cooler = F.SubModelGroup(TC.Condenser, 'FG', label = 'Cooler')
	recuperator = F.SubModelGroup(TC.HeatExchangerTwoStreams, 'FG', label = 'Recuperator')
	throttleValve = F.SubModelGroup(TC.ThrottleValve, 'FG', label = 'JT valve')
#	evaporator = F.SubModelGroup(TC.Evaporator, 'FG', label = 'Evaporator')
	inputs = F.SuperGroup(['workingFluidGroup', compressor, cooler, recuperator, throttleValve], label = 'Cycle definition')

	#---------------- Actions ----------------#
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
# 	exampleAction = ServerAction("loadEg", label = "Examples", options = (
# 			('R134aCycle', 'Typical fridge with R134a as a refrigerant'),
# 			('CO2TranscriticalCycle', 'CO2 transcritial cycle'),
# 	))
	inputActionBar = ActionBar([computeAction], save = True)
	#--------------- Model view ---------------#
	inputView = F.ModelView(ioType = "input", superGroups = [inputs, 'cycleDiagram'], 
		actionBar = inputActionBar, autoFetch = True)	

	#================ Results ================#
	compressorPower = F.Quantity('Power', default = (1, 'kW'), label = 'compressor power')
	condenserHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'condenser heat out')
	evaporatorHeat = F.Quantity('HeatFlowRate', default = (1, 'kW'), label = 'evaporator heat in')
	flowFieldGroup = F.FieldGroup([compressorPower, condenserHeat, evaporatorHeat], label = 'Energy flows')
	resultEnergy = F.SuperGroup([flowFieldGroup, 'efficiencyFieldGroup'], label = 'Energy')
	resultView = F.ModelView(ioType = "output", superGroups = ['resultDiagrams', 'resultStates', resultEnergy])

	#============= Page structure =============#
	modelBlocks = [inputView, resultView]

	#================ Methods ================#
	