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
	
from .models import CompressionExpansion, HeatingCooling
@registerView(router)
class ThermodynamicProcessView(ModularPageView):
	label = "Thermodynamic processes"
	modules = [CompressionExpansion, HeatingCooling]

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

from .models.lib.ThermodynamicComponents import ThermodynamicComponentsDoc
@registerView(router)
class ThermodynamicComponents(ModularPageView):
	label = "Thermodynamic components (Doc)"
	modules = [ThermodynamicComponentsDoc]
	

@registerView(router)
class HeatingCoolingCyces(ModularPageView):
	label = "Heating/cooling cycles"
	modules = [M.VaporCompressionCycle, M.VaporCompressionCycleWithRecuperator, M.HeatPumpCyclesDoc]	
	requireGoogle = ['visualization']

@registerView(router)
class PowerGenerationCycles(ModularPageView):
	label = "Power generation cycles"
	modules = [M.RankineCycle, M.RegenerativeRankineCycle, M.HeatEngineCyclesDoc]
	requireGoogle = ['visualization']
	
@registerView(router)
class HeatExchange1DView(ModularPageView):
	label = "Heat exchange 1D"
	modules = [M.CryogenicPipe, M.CableHeating1D]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
