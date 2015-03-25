from smo.web.view import ModularPageView
from smo.web.view import action
from smo.web.router import ViewRouter, registerView
from pymongo import MongoClient
import ThermoFluids

mongoClient = MongoClient()

router = ViewRouter('ThermoFluids', ThermoFluids)

from .models import PropertyCalculatorCoolprop, FluidInfo, SaturationData, PHDiagramModel, FluidPropertiesDoc
@registerView(router)
class FluidPropsCalculatorView(ModularPageView):
	label = 'Fluid properties (CoolProp)'
	modules = [PropertyCalculatorCoolprop, FluidInfo, SaturationData, PHDiagramModel, FluidPropertiesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	
# 	@action.post()	
# 	def computeFluidProps(self, model, view, parameters):		
# 		fpc = PropertyCalculatorCoolprop()
# 		fpc.fieldValuesFromJson(parameters)
# 		fpc.compute()
# 		if (fpc.isTwoPhase):
# 			a =  fpc.modelView2Json('resultViewIsTwoPhase')
# 			print a['definitions'][1]['groups'][0]['name']
# 			return a
# 		else:
# 			return fpc.modelView2Json('resultView')
	
from .models import CompressionExpansionModel, HeatingCoolingModel
@registerView(router)
class ThermodynamicProcessView(ModularPageView):
	label = "Thermodynamic processes"
	modules = [CompressionExpansionModel, HeatingCoolingModel]

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

from .models import ReverseBraytonCycle, ReverseBraytonCycleWithRecurperator
@registerView(router)
class HeatingCoolingCyces(ModularPageView):
	label = "Heating/cooling cycles"
	modules = [ReverseBraytonCycle, ReverseBraytonCycleWithRecurperator]	
	requireGoogle = ['visualization']

from .models import RankineCycle, RankineCycleWithRecurperator
@registerView(router)
class PowerGenerationCycles(ModularPageView):
	label = "Power generation cycles"
	modules = [RankineCycle, RankineCycleWithRecurperator]
	requireGoogle = ['visualization']
	
from .models import CryogenicPipe
from .models import CableHeating1D
@registerView(router)
class HeatExchange1DView(ModularPageView):
	label = "Heat exchange 1D"
	modules = [CryogenicPipe, CableHeating1D]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
