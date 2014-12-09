import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from smo.numerical_model.quantity import Quantities
from smo.smoflow3d.SimpleMaterials import Fluids
from collections import OrderedDict
from smo.django.view import SmoJsonResponse, View
from smo.django.view import action as smo_action

from smo.smoflow3d.calculators.FluidPropsCalculator import FluidPropsCalculator, FluidInfo, SaturationData
class FluidPropsCalculatorView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/FluidPropsCalculator.html', locals(), 
				context_instance=RequestContext(request))
	
	@smo_action('post')
	def getInputs(self, parameters):	
		fpc = FluidPropsCalculator()
		return fpc.superGroupList2Json([fpc.inputs])
	
	@smo_action('post')
	def compute(self, parameters):
		fpc = FluidPropsCalculator()
		fpc.fieldValuesFromJson(parameters)
		fpc.compute()
		return fpc.superGroupList2Json([fpc.results])
	
	@smo_action('post')
	def getFluidInfo(self, parameters):
		return FluidInfo.getFluidInfo()
	
	@smo_action('post')
	def getFluidList(self, parameters):
		return FluidInfo.getFluidList()
	
	@smo_action('post')
	def getSaturationData(self, parameters):
		sd = SaturationData(parameters['fluidName'])
		return sd.getSaturationData()

from smo.simple_flow.FlowResistance import Pipe 
class FlowResistanceView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/FlowResistance.html', locals(), 
				context_instance=RequestContext(request))
	
	@smo_action('post')
	def getFlowResistanceInputs(self, parameters):
		pipe = Pipe()
		return pipe.superGroupList2Json([Pipe.inputs])
	
	@smo_action('post')	
	def computeFlowResistance(self, parameters):
		pipe = Pipe()
		pipe.fieldValuesFromJson(parameters)
		pipe.computeGeometry()
		pipe.computePressureDrop()
		return pipe.superGroupList2Json([Pipe.results])

from smo.simple_flow.FreeConvection import FreeConvection_External
from smo.simple_flow.FreeConvection import FreeConvection_Internal
class FreeConvectionView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/FreeConvection.html', locals(), 
				context_instance=RequestContext(request))
	
	@smo_action('post')
	def getConvectionExternalInputs(self, parameters):
		convection = FreeConvection_External()
		return convection.superGroupList2Json([convection.inputs])
	
	@smo_action('post')
	def getConvectionInternalInputs(self, parameters):
		convection = FreeConvection_Internal()
		return convection.superGroupList2Json([convection.inputs])
	
	@smo_action('post')	
	def computeConvectionInternal(self, parameters):
		convection = FreeConvection_Internal()
		convection.fieldValuesFromJson(parameters)
		convection.compute()
		return convection.superGroupList2Json([convection.results])
	
	@smo_action('post')	
	def computeConvectionExternal(self, parameters):
		convection = FreeConvection_External()
		convection.fieldValuesFromJson(parameters)
		convection.compute()
		return convection.superGroupList2Json([convection.results])
	
from smo.simple_flow.CryogenicInsulation import GasConduction
class CryogenicInsulation(View):	
	def get(self, request):
		return render_to_response('ThermoFluids/CryogenicInsulation.html', locals(), 
				context_instance=RequestContext(request))

	@smo_action('post')
	def getCryogenicInsulationInputs(self, parameters):
		gc = GasConduction()
		return gc.superGroupList2Json([gc.inputs])
	
	@smo_action('post')
	def computeCryogenicInsulation(self, parameters):
		gc = GasConduction()
		gc.fieldValuesFromJson(parameters)
		gc.compute()		
		return gc.superGroupList2Json([gc.results])
	
from smo.smoflow3d.calculators.CycleCalculator import HeatPumpCalculator
class HeatPumpView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/HeatPump.html', locals(), 
				context_instance=RequestContext(request))
	
	@smo_action('post')
	def getHeatPumpInputs(self, parameters):
		hpc = HeatPumpCalculator()
		return hpc.superGroupList2Json([hpc.inputs])
	
	@smo_action('post')	
	def computeHeatPump(self, parameters):
		hpc = HeatPumpCalculator()
		hpc.fieldValuesFromJson(parameters)
		hpc.compute()
		return hpc.superGroupList2Json([hpc.results])

from smo.simple_flow.WireHeating import WireHeating1D
class HeatExchange1DView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/HeatExchange1D.html', locals(), 
				context_instance=RequestContext(request))
	
	@smo_action('post')
	def getWireHeatingInputs(self, parameters):
		wireHeating = WireHeating1D()
		return wireHeating.superGroupList2Json([wireHeating.inputs])
	
	@smo_action('post')
	def computeWireHeating(self, parameters):
		wireHeating = WireHeating1D()
		wireHeating.fieldValuesFromJson(parameters)
		wireHeating.compute()
		return wireHeating.superGroupList2Json([wireHeating.results])

class TestView(View):
	def get(self, request):
		return render_to_response('ThermoFluids/TestView.html', locals(), 
				context_instance=RequestContext(request))
	
	@smo_action('post')
	def getInputs(self, parameters):
		return Quantities
		
		
		
