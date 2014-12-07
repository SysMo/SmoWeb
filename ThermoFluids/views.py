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
	def getInputs(self, parameters):
		pipe = Pipe()
		return pipe.superGroupList2Json([Pipe.inputs])
	
	@smo_action('post')	
	def compute(self, parameters):
		pipe = Pipe()
		pipe.fieldValuesFromJson(parameters)
		pipe.computeGeometry()
		pipe.computePressureDrop()
		return pipe.superGroupList2Json([Pipe.results])

def freeConvectionView(request):
	from smo.simple_flow.FreeConvection import FreeConvection_External
	from smo.simple_flow.FreeConvection import FreeConvection_Internal
	if request.method == 'POST':
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs_Internal'):
			with SmoJsonResponse() as response:
				convection = FreeConvection_Internal()
				response.set(convection.superGroupList2Json([convection.inputs]))
			return response.json()
		elif (action == 'compute_Internal'):
			with SmoJsonResponse() as response:
				convection = FreeConvection_Internal()
				convection.fieldValuesFromJson(parameters)
				convection.compute()
				response.set(convection.superGroupList2Json([convection.results]))
			return response.json()
		if (action == 'getInputs_External'):
			with SmoJsonResponse() as response:
				convection = FreeConvection_External()
				response.set(convection.superGroupList2Json([convection.inputs]))
			return response.json()
		elif (action == 'compute_External'):
			with SmoJsonResponse() as response:
				convection = FreeConvection_External()
				convection.fieldValuesFromJson(parameters)
				convection.compute()
				response.set(convection.superGroupList2Json([convection.results]))
			return response.json()
		else:
			raise ValueError('Unknown action "{0}"'.format(action)) 
	else:
		return render_to_response('ThermoFluids/FreeConvection.html', locals(), 
				context_instance=RequestContext(request))
	
def heatPumpView(request):
	if request.method == 'GET':
		return render_to_response('ThermoFluids/HeatPump.html', locals(), 
				context_instance=RequestContext(request))
	elif request.method == 'POST':
		from smo.smoflow3d.calculators.CycleCalculator import HeatPumpCalculator 
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			hpc = HeatPumpCalculator()
			inputs = hpc.superGroupList2Json([hpc.inputs])
			return JsonResponse(inputs)
		elif (action == 'compute'):
			with SmoJsonResponse() as response:
				hpc = HeatPumpCalculator()
				hpc.fieldValuesFromJson(parameters)
				hpc.compute()
				response.set(hpc.superGroupList2Json([hpc.results])) 
			return response.json()

		else:
			raise ValueError('Unknown post action "{0}" for URL: {1}'.format(action, 'ThermoFluids/HeatPump.html'))

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
	
def testView(request):
	if request.method == 'GET':
		return render_to_response('ThermoFluids/TestView.html', 
								context_instance=RequestContext(request))
	elif request.method == 'POST':
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			return JsonResponse(Quantities)
		else:
			raise ValueError('Unknown post action "{0}" for URL: {1}'.format(action, 'ThermoFluids/TestView.html'))
		
		
		
