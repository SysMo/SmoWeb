import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from smo.model.quantity import Quantities
from smo.media.MaterialData import Fluids
from collections import OrderedDict
from smo.django.view import ModularPageView
from smo.django.view import action
from smo.django.router import ViewRouter, registerView
import tasks

from pymongo import MongoClient
from bson.objectid import ObjectId
mongoClient = MongoClient()

router = ViewRouter('ThermoFluids')

from smo.media.calculators.FluidPropsCalculator import FluidProperties, FluidInfo, SaturationData
#@registerView(router)
class FluidPropsCalculatorView(ModularPageView):
	name = 'FluidPropsCalculator'
	label = 'Fluid properties (CoolProp)'
	modules = [FluidProperties, FluidInfo, SaturationData]
	def get(self, request):
		return render_to_response('ThermoFluids/FluidProperties.html', locals(), 
				context_instance=RequestContext(request))
	
	@action.post()	
	def computeFluidProps(self, model, view, parameters):		
		fpc = FluidProperties()
		print parameters
		fpc.fieldValuesFromJson(parameters)
		fpc.compute()
		if (fpc.isTwoPhase == True):
			return fpc.modelView2Json(fpc.resultViewIsTwoPhase)
		else:
			return fpc.modelView2Json(fpc.resultView)
	
	@action.post()
	def getFluidInfo(self, model, view, parameters):
		return FluidInfo.getFluidInfo() 

	@action.post()
	def getFluidList(self, model, view, parameters):
		return FluidInfo.getFluidList()
	

from smo.flow.FlowResistance import PipeFlow, PipeFlowDoc
@registerView(router)
class FlowResistanceView(ModularPageView):
	name = "FlowResistance"
	label = "Flow resistance"
	modules = [PipeFlow, PipeFlowDoc]

from smo.flow.FreeConvection import FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc
@registerView(router)
class FreeConvectionView(ModularPageView):
	name = "FreeConvection"
	label = "Free convection"
	modules = [FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc]

from smo.media.calculators.CycleCalculator import HeatPump
@registerView(router)
class HeatPumpView(ModularPageView):
	name = "HeatPump"
	label = "Heat pump"
	modules = [HeatPump]	
	
from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
from smo.flow.heatExchange1D.CableHeating import CableHeating1D
@registerView(router)
class HeatExchange1DView(ModularPageView):
	name = "HeatExchange1D"
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
	
