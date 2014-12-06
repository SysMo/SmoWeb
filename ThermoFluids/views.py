import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from smo.numerical_model.quantity import Quantities
from smo.smoflow3d.SimpleMaterials import Fluids
from collections import OrderedDict
from smo.django.view import SmoJsonResponse, View
from smo.django.view import action as smo_action

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

def fluidPropsCalculatorView(request):
	if request.method == 'GET':
		return render_to_response('ThermoFluids/FluidPropsCalculator.html', locals(), 
				context_instance=RequestContext(request))
	elif request.method == 'POST':
		from smo.smoflow3d.calculators.FluidPropsCalculator import FluidPropsCalculator, FluidInfo, SaturationData
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			fpc = FluidPropsCalculator()
			inputs = fpc.superGroupList2Json([fpc.inputs])
			return JsonResponse(inputs)
		elif (action == 'getFluidInfo'):
			fluidInformation = FluidInfo.getFluidInfo()
			return JsonResponse(fluidInformation, safe = False)
		elif (action == 'getFluidList'):
			fluidList = FluidInfo.getFluidList()
			return JsonResponse(fluidList, safe = False)
		elif (action == 'getSaturationData'):
			sd = SaturationData(parameters['fluidName'])
			satData = sd.getSaturationData()
			return JsonResponse(satData, safe = False)
		elif (action == 'compute'):
			with SmoJsonResponse() as response:
				fpc = FluidPropsCalculator()
				fpc.fieldValuesFromJson(parameters)
				fpc.compute()
				response.set(fpc.superGroupList2Json([fpc.results]))
			return response.json()
		else:
			raise ValueError('Unknown post action "{0}" for URL: {1}'.format(action, 'ThermoFluids/FluidPropsCalculator.html'))

def flowResistanceView(request):
	if request.method == 'POST':
		from smo.simple_flow.FlowResistance import Pipe
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			inputs = {}
			with SmoJsonResponse() as response:
				pipe = Pipe()
				inputs = pipe.superGroupList2Json([Pipe.inputs])
				response.set(inputs)
			return response.json()
		elif (action == 'compute'):
			with SmoJsonResponse() as response:
				pipe = Pipe()
				pipe.fieldValuesFromJson(parameters)
				pipe.computeGeometry()
				pipe.computePressureDrop()
				response.set(pipe.superGroupList2Json([Pipe.results]))
			return response.json()
		else:
			raise ValueError('Unknown action "{0}"'.format(action)) 
	else:
		return render_to_response('ThermoFluids/FlowResistance.html', locals(), 
				context_instance=RequestContext(request))

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
		
		
		
