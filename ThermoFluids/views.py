import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

def heatPumpView(request):
	if request.method == 'GET':
		return render_to_response('ThermoFluids/HeatPump.html', locals(), 
				context_instance=RequestContext(request))
	elif request.method == 'POST':
		from smo.smoflow3d.CycleCalculator import HeatPumpCalculator 
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
		from smo.smoflow3d.FluidPropsCalculator import FluidPropsCalculator 
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			fpc = FluidPropsCalculator()
			inputs = fpc.superGroupList2Json([fpc.inputs])
			return JsonResponse(inputs)
		elif (action == 'compute'):
			fpc = FluidPropsCalculator()
			fpc.fieldValuesFromJson(parameters)
			fpc.compute()
			results = fpc.superGroupList2Json([fpc.results]) 
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
			pipe = Pipe()
			inputs = pipe.superGroupList2Json([Pipe.inputs])
			return JsonResponse(inputs)
		elif (action == 'compute'):
			pipe = Pipe()
			pipe.fieldValuesFromJson(parameters)
			pipe.computeGeometry()
			pipe.computePressureDrop()
			results = pipe.superGroupList2Json([Pipe.results]) 
			return JsonResponse(results)
		else:
			raise ValueError('Unknown action "{0}"'.format(action)) 
	else:
		return render_to_response('ThermoFluids/FlowResistance.html', locals(), 
				context_instance=RequestContext(request))
		
def testView(request):
	return render_to_response('ThermoFluids/TestView.html', context_instance=RequestContext(request))