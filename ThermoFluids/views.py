import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from smo.model.quantity import Quantities
from smo.media.SimpleMaterials import Fluids
from collections import OrderedDict
from smo.django.view import SmoJsonResponse, View
from smo.django.view import action
import tasks

from pymongo import MongoClient
from bson.objectid import ObjectId
mongoClient = MongoClient()


from smo.media.calculators.FluidPropsCalculator import FluidPropsCalculator, FluidInfo, SaturationData
class FluidPropsCalculatorView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/FluidPropsCalculator.html', locals(), 
				context_instance=RequestContext(request))
	
	@action('post')
	def getInputs(self, parameters):	
		fpc = FluidPropsCalculator()
		return fpc.superGroupList2Json([fpc.inputs])
	
	@action('post')
	def compute(self, parameters):
		fpc = FluidPropsCalculator()
		fpc.fieldValuesFromJson(parameters)
		fpc.compute()
		if (fpc.isTwoPhase == True):
			return fpc.superGroupList2Json([fpc.props, fpc.saturationProps])
		else:
			return fpc.superGroupList2Json([fpc.props])
	
	@action('post')
	def getFluidInfo(self, parameters):
		return FluidInfo.getFluidInfo()
	
	@action('post')
	def getFluidList(self, parameters):
		return FluidInfo.getFluidList()
	
	@action('post')
	def getSaturationData(self, parameters):
		sd = SaturationData()
		sd.fieldValuesFromJson(parameters)
		sd.compute()
		return sd.superGroupList2Json([sd.satSuperGroup])

from smo.flow.FlowResistance import PipeFlow, PipeFlowDoc
class FlowResistanceView(View):
	modules = [PipeFlow, PipeFlowDoc]
	appName = "FlowResistance"
	controllerName = "FlowResistanceController"
	
	def get(self, request):
		return render_to_response('ModelViewTemplate.html', {"view": self}, 
				context_instance=RequestContext(request))
	
	@action('post')	
	def computeFlowResistance(self, model, view, parameters):
		pipe = PipeFlow()
		pipe.fieldValuesFromJson(parameters)
		pipe.computeGeometry()
		pipe.computePressureDrop()
		return pipe.modelView2Json(view)

from smo.flow.FreeConvection import FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc
class FreeConvectionView(View):
	modules = [FreeConvection_External, FreeConvection_Internal, FreeConvectionDoc]
	appName = "FreeConvection"
	controllerName = "FreeConvectionController"
	
	def get(self, request):
		return render_to_response('ModelViewTemplate.html', {"view": self}, 
				context_instance=RequestContext(request))
	
from smo.flow.CryogenicInsulation import GasConduction
class CryogenicInsulation(View):	
	def get(self, request):
		return render_to_response('ThermoFluids/CryogenicInsulation.html', locals(), 
				context_instance=RequestContext(request))

	@action('post')
	def getCryogenicInsulationInputs(self, parameters):
		gc = GasConduction()
		return gc.superGroupList2Json([gc.inputs])
	
	@action('post')
	def computeCryogenicInsulation(self, parameters):
		gc = GasConduction()
		gc.fieldValuesFromJson(parameters)
		gc.compute()		
		return gc.superGroupList2Json([gc.results])
	
from smo.media.calculators.CycleCalculator import HeatPump
class HeatPumpView(View):
	modules = [HeatPump]	
	appName = "HeatPump"
	controllerName = "HeatPumpController"
	
	def get(self, request):
		return render_to_response('ModelViewTemplate.html', {"view": self}, 
				context_instance=RequestContext(request))
	
# 	@action('post')
# 	def getHeatPumpInputs(self, parameters):
# 		hpc = HeatPump()
# 		return hpc.superGroupList2Json([hpc.inputs])
# 	
# 	@action('post')	
# 	def computeHeatPump(self, parameters):
# 		hpc = HeatPump()
# 		hpc.fieldValuesFromJson(parameters)
# 		hpc.compute()
# 		return hpc.superGroupList2Json([hpc.results])

from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
class HeatExchange1DView(View):
	modules = [CryogenicPipe]	
	appName = "HeatExchange1D"
	controllerName = "HeatExchange1DController"
	def get(self, request):
		self.activeModule = CryogenicPipe
		jsLibraries = ['dygraph', 'dygraphExport']
		googleModules = {'visualization':{'version': '1.0', 'packages': ["corechart", "table", "controls"]}}
		return render_to_response('ModelViewTemplate.html', 
				{'view': self, 'jsLibraries': jsLibraries, 'googleModules': googleModules},
				context_instance=RequestContext(request))
		

from smo.flow.TestModel import TestModel
class TestView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/TestView.html', locals(), 
				context_instance=RequestContext(request))
	
	@action('post')
	def getInputs(self, parameters):
		testModel = TestModel()
		return testModel.superGroupList2Json([testModel.inputs])

	@action('post')
	def compute(self, parameters):
		testModel = TestModel()
		testModel.fieldValuesFromJson(parameters)
		testModel.compute()
		return testModel.superGroupList2Json([testModel.results])

class ExampleView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/HeatExchange1D.html', locals(), 
				context_instance=RequestContext(request))
		
	@action('post')
	def getCryogenicPipeInputs(self, parameters):
		from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
		pipe = CryogenicPipe()
		return pipe.superGroupList2Json([pipe.inputValues, pipe.settings])
	
	@action('post')
	def computeCryogenicPipe(self, parameters):
		from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
		result = tasks.Celery_compute.delay(CryogenicPipe, parameters)
		result = tasks.Celery_compute(CryogenicPipe, parameters)
		return result.get(timeout = 10)
		
