from smo.web.view import ModularPageView
from smo.web.router import ViewRouter, registerView
from pymongo import MongoClient
import ThermoFluids
import models as M

mongoClient = MongoClient()

router = ViewRouter('ThermoFluids', ThermoFluids)

from .models import PropertyCalculatorCoolprop, FluidInfo, SaturationData, PHDiagram, FluidPropertiesDoc
@registerView(router)
class FluidPropsCalculatorView(ModularPageView):
	label = 'Fluid properties (CoolProp)'
	modules = [PropertyCalculatorCoolprop, FluidInfo, SaturationData, PHDiagram, FluidPropertiesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	
from .models.ThermodynamicProcesses import Compression, Expansion, Heating, Cooling, HeatExchangerTwoStreams
from .models.lib.ThermodynamicComponents import ThermodynamicComponentsDoc
@registerView(router)
class ThermodynamicProcessView(ModularPageView):
	label = "Thermodynamic processes and components"
	requireGoogle = ['visualization']
	modules = [Compression, Expansion, Heating, Cooling, HeatExchangerTwoStreams, ThermodynamicComponentsDoc]

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

# @registerView(router)
# class ThermodynamicComponents(ModularPageView):
# 	label = "Thermodynamic components (Doc)"
# 	modules = [ThermodynamicComponentsDoc]
# 	

@registerView(router)
class HeatingCoolingCyces(ModularPageView):
	label = "Heating/cooling cycles"
	modules = [M.VaporCompressionCycle, M.VaporCompressionCycleWithRecuperator, M.HeatPumpCyclesDoc]
	requireJS = ['dygraph', 'dygraphExport']	
	requireGoogle = ['visualization']

@registerView(router)
class PowerGenerationCycles(ModularPageView):
	label = "Power generation cycles"
	modules = [M.RankineCycle, M.RegenerativeRankineCycle, M.HeatEngineCyclesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	
@registerView(router)
class LiquefactionCycles(ModularPageView):
	label = "Liquefaction cycles"
	modules = [M.LindeHampsonCycle, M.ClaudeCycle, M.LiquefactionCyclesDoc]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

@registerView(router)
class HeatExchange1DView(ModularPageView):
	label = "Heat exchange 1D"
	modules = [M.CryogenicPipe, M.CableHeating1D]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

@registerView(router)
class CompressedGasStorageView(ModularPageView):
	label = "Compressed Gas Storage"
	modules = [M.CompressedGasStorage, M.CompressedGasStorageDoc]	
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

@registerView(router)
class HeatExchangerDesignView(ModularPageView):
	label = 'Heat exchanger design'
	modules = [M.CylindricalBlockHeatExchanger]
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']

from models.TestModule import ABC
@registerView(router)
class TestPage(ModularPageView):
	showInMenu = False
	label = 'Test'
	requireJS = ['dygraph', 'dygraphExport']
	requireGoogle = ['visualization']
	modules = [ABC]

from django.http import HttpResponseRedirect, HttpResponse
from celery.result import AsyncResult
import json
from ThermoFluids.tasks import do_work

def start_job(request):
	job = do_work.delay()
	#return HttpResponseRedirect('ThermoFluids/CheckProgress' + '?job=' + job.id)
	return HttpResponse(json.dumps({'data' : {'job': job.id}}))

def check_progress(request):
	postData = json.loads(request.body)
	job_id = postData['data']['parameters']
	
	job = AsyncResult(job_id)
	resp = {'data': {}}
	resp['data']['job'] = job_id
	try:
		resp['data']['progressValue'] = round(job.info['current']/job.info['total'] * 100, 0)
	except:
		resp['data']['progressValue'] = 100
	return HttpResponse(json.dumps(resp), content_type='text/plain')