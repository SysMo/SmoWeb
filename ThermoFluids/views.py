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

from smo.flow.FlowResistance import Pipe 
class FlowResistanceView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/FlowResistance.html', locals(), 
				context_instance=RequestContext(request))
	
	@action('post')
	def getFlowResistanceInputs(self, parameters):
		pipe = Pipe()
		return pipe.superGroupList2Json([Pipe.inputs])
	
	@action('post')	
	def computeFlowResistance(self, parameters):
		pipe = Pipe()
		pipe.fieldValuesFromJson(parameters)
		pipe.computeGeometry()
		pipe.computePressureDrop()
		return pipe.superGroupList2Json([Pipe.results])

from smo.flow.FreeConvection import FreeConvection_External
from smo.flow.FreeConvection import FreeConvection_Internal
class FreeConvectionView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/FreeConvection.html', locals(), 
				context_instance=RequestContext(request))
	
	@action('post')
	def getConvectionExternalInputs(self, parameters):
		convection = FreeConvection_External()
		return convection.superGroupList2Json([convection.inputs])
	
	@action('post')
	def getConvectionInternalInputs(self, parameters):
		convection = FreeConvection_Internal()
		return convection.superGroupList2Json([convection.inputs])
	
	@action('post')	
	def computeConvectionInternal(self, parameters):
		convection = FreeConvection_Internal()
		convection.fieldValuesFromJson(parameters)
		convection.compute()
		return convection.superGroupList2Json([convection.results])
	
	@action('post')	
	def computeConvectionExternal(self, parameters):
		convection = FreeConvection_External()
		convection.fieldValuesFromJson(parameters)
		convection.compute()
		return convection.superGroupList2Json([convection.results])
	
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
	
from smo.media.calculators.CycleCalculator import HeatPumpCalculator
class HeatPumpView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/HeatPump.html', locals(), 
				context_instance=RequestContext(request))
	
	@action('post')
	def getHeatPumpInputs(self, parameters):
		hpc = HeatPumpCalculator()
		return hpc.superGroupList2Json([hpc.inputs])
	
	@action('post')	
	def computeHeatPump(self, parameters):
		hpc = HeatPumpCalculator()
		hpc.fieldValuesFromJson(parameters)
		hpc.compute()
		return hpc.superGroupList2Json([hpc.results])

from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
from smo.flow.heatExchange1D.CableHeating import CableHeating1D
class HeatExchange1DView(View):
	modules = [CryogenicPipe, CableHeating1D]	
	appName = "HeatExchange1D"
	controllerName = "HeatExchange1DController"
	def get(self, request):
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
		
