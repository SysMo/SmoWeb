import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from smo.numerical_model.quantity import Quantities
from smo.smoflow3d.SimpleMaterials import Fluids
from collections import OrderedDict

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
			hpc = HeatPumpCalculator()
			hpc.fieldValuesFromJson(parameters)
			hpc.compute()
			results = hpc.superGroupList2Json([hpc.results]) 
			return JsonResponse(results)

		else:
			raise ValueError('Unknown post action "{0}" for URL: {1}'.format(action, 'ThermoFluids/HeatPump.html'))

def fluidPropsCalculatorView(request):
	if request.method == 'GET':
		return render_to_response('ThermoFluids/FluidPropsCalculator.html', locals(), 
				context_instance=RequestContext(request))
	elif request.method == 'POST':
		from smo.smoflow3d.calculators.FluidPropsCalculator import FluidPropsCalculator, FluidInfo
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			fpc = FluidPropsCalculator()
			inputs = fpc.superGroupList2Json([fpc.inputs])
			return JsonResponse(inputs)
		elif (action == 'getFluidInfo'):
			fluidDataList = FluidInfo.getList()
			return JsonResponse(fluidDataList, safe = False)
		elif (action == 'compute'):
			results = {}
			try: 
				fpc = FluidPropsCalculator()
				fpc.fieldValuesFromJson(parameters)
				fpc.compute()
				results = fpc.superGroupList2Json([fpc.results])
				results['errStatus'] = False
				return JsonResponse(results)
			except Exception, e:
				results['errStatus'] = True
				results['error'] = str(e)
				return JsonResponse(results)
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
			try:
				pipe = Pipe()
				inputs = pipe.superGroupList2Json([Pipe.inputs])
				return JsonResponse(inputs)
			except Exception, e:
				inputs['errStatus'] = True
				inputs['error'] = str(e)
				return JsonResponse(inputs)
		elif (action == 'compute'):
			results = {}
			try:
				pipe = Pipe()
				pipe.fieldValuesFromJson(parameters)
				pipe.computeGeometry()
				pipe.computePressureDrop()
				results = pipe.superGroupList2Json([Pipe.results])
				results['errStatus'] = False 
				return JsonResponse(results)
			except Exception, e:
				results['errStatus'] = True
				results['error'] = str(e)
				return JsonResponse(results)
		else:
			raise ValueError('Unknown action "{0}"'.format(action)) 
	else:
		return render_to_response('ThermoFluids/FlowResistance.html', locals(), 
				context_instance=RequestContext(request))

def freeConvectionView(request):
	from smo.simple_flow.FreeConvection import FreeConvection
	if request.method == 'POST':
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			inputs = {}
			convection = FreeConvection()
			inputs = convection.superGroupList2Json([convection.inputs])
			return JsonResponse(inputs)
		elif (action == 'compute'):
			pass
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
		
		
		
