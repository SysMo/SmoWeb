from smo.web.view import ModularPageView
from smo.web.router import ViewRouter, registerView
from pymongo import MongoClient
import ThermoFluids
import models as M

mongoClient = MongoClient()

router = ViewRouter('ThermoFluids', ThermoFluids)

from .models import PropertyCalculatorCoolprop, FluidInfo, SaturationData, PHDiagram, FluidPropertiesDoc
@registerView(router)
class FluidPropsCalculatorView(ModularPageView):
	label = 'Fluid properties (CoolProp)'
	modules = [PropertyCalculatorCoolprop, FluidInfo, SaturationData, PHDiagram, FluidPropertiesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	
from .models.ThermodynamicProcesses import Compression, Expansion, Heating, Cooling, HeatExchangerTwoStreams
from .models.lib.ThermodynamicComponents import ThermodynamicComponentsDoc
@registerView(router)
class ThermodynamicProcessView(ModularPageView):
	label = "Thermodynamic processes and components"
	requireGoogle = ['visualization']
	modules = [Compression, Expansion, Heating, Cooling, HeatExchangerTwoStreams, ThermodynamicComponentsDoc]

from .models import PipeFlow, PipeFlowDoc
@registerView(router)
class PipeFlowView(ModularPageView):
	label = "Pipe flow"
	modules = [PipeFlow, PipeFlowDoc]

from .models import FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc
@registerView(router)
class FreeConvectionView(ModularPageView):
	label = "Free convection"
	modules = [FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc]

@registerView(router)
class HeatingCoolingCyces(ModularPageView):
	label = "Heating/cooling cycles"
	modules = [M.VaporCompressionCycle, M.VaporCompressionCycleWithRecuperator, M.HeatPumpCyclesDoc]
	requireJS = ['dygraph', 'dygraphExport']	
	requireGoogle = ['visualization']

@registerView(router)
class PowerGenerationCycles(ModularPageView):
	label = "Power generation cycles"
	modules = [M.RankineCycle, M.RegenerativeRankineCycle, M.HeatEngineCyclesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	
@registerView(router)
class LiquefactionCycles(ModularPageView):
	label = "Liquefaction cycles"
	modules = [M.LindeHampsonCycle, M.ClaudeCycle, M.LiquefactionCyclesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

@registerView(router)
class HeatExchange1DView(ModularPageView):
	label = "Heat exchange 1D"
	modules = [M.CryogenicPipe, M.CableHeating1D]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

@registerView(router)
class CompressedGasStorageView(ModularPageView):
	label = "Compressed Gas Storage"
	modules = [M.CompressedGasStorage, M.CompressedGasStorageDoc]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

@registerView(router)
class HeatExchangerDesignView(ModularPageView):
	label = 'Heat exchanger design'
	modules = [M.CylindricalBlockHeatExchanger]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

from models.TestModule import ABC
@registerView(router)
class TestPage(ModularPageView):
	showInMenu = False
	label = 'Test'
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	modules = [ABC]