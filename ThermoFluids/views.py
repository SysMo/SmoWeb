from smo.web.view import ModularPageView
from smo.web.view import action
from smo.web.router import ViewRouter, registerView
from pymongo import MongoClient
import ThermoFluids

mongoClient = MongoClient()

router = ViewRouter('ThermoFluids', ThermoFluids)

from smo.media.calculators.FluidPropsCalculator import PropertyCalculatorCoolprop, FluidInfo, SaturationData,\
FluidPropertiesDoc
@registerView(router)
class FluidPropsCalculatorView(ModularPageView):
	label = 'Fluid properties (CoolProp)'
	modules = [PropertyCalculatorCoolprop, FluidInfo, SaturationData, FluidPropertiesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	
	@action.post()	
	def computeFluidProps(self, model, view, parameters):		
		fpc = PropertyCalculatorCoolprop()
		fpc.fieldValuesFromJson(parameters)
		fpc.compute()
		if (fpc.isTwoPhase == True):
			return fpc.modelView2Json(fpc.resultViewIsTwoPhase)
		else:
			return fpc.modelView2Json(fpc.resultView)
	
from smo.media.calculators.ThermodynamicProcess import ThermodynamicProcess
@registerView(router)
class ThermodynamicProcessView(ModularPageView):
	label = "Thermodynamic processes"
	modules = [ThermodynamicProcess]

from .models.PipeFlowModel import PipeFlowModel, PipeFlowDoc
@registerView(router)
class PipeFlowView(ModularPageView):
	label = "Pipe flow"
	modules = [PipeFlowModel, PipeFlowDoc]

from smo.flow.FreeConvection import FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc
@registerView(router)
class FreeConvectionView(ModularPageView):
	label = "Free convection"
	modules = [FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc]

from smo.media.calculators.CycleCalculator import HeatPump
@registerView(router)
class HeatPumpView(ModularPageView):
	label = "Heat pump"
	modules = [HeatPump]	
	
from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
from smo.flow.heatExchange1D.CableHeating import CableHeating1D
@registerView(router)
class HeatExchange1DView(ModularPageView):
	label = "Heat exchange 1D"
	modules = [CryogenicPipe, CableHeating1D]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

		
# from smo.flow.CryogenicInsulation import GasConduction
# class CryogenicInsulation(ModularPageView):	
# 	def get(self, request):
# 		return render_to_response('ThermoFluids/CryogenicInsulation.html', locals(), 
# 				context_instance=RequestContext(request))
# 
# 	@action.post()
# 	def getCryogenicInsulationInputs(self, parameters):
# 		gc = GasConduction()
# 		return gc.superGroupList2Json([gc.inputs])
# 	
# 	@action.post()
# 	def computeCryogenicInsulation(self, parameters):
# 		gc = GasConduction()
# 		gc.fieldValuesFromJson(parameters)
# 		gc.compute()		
# 		return gc.superGroupList2Json([gc.results])
	
