from django.views.generic import TemplateView
from django.core.context_processors import csrf

from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from  SmoWeb.settings import MEDIA_ROOT, hdfFileFolder
import json
from django.views.decorators.csrf import csrf_protect
from smo.smoflow3d.SimpleMaterials import Solids
# Create your views here.

#from django.db.models import Model 

class FluidPropertiesCoolPropView(TemplateView):
	template_name = "ThermoFluids/FluidPropertiesCoolProp.html"
	def get(self, request):
#		form = FluidPropertiesCoolPropForm()
		
		return render_to_response(self.template_name, locals(), 
				context_instance=RequestContext(self.request))
		
	def post(self, request):
#		form = FluidPropertiesCoolPropForm(self.request.POST)
# 		if not form.is_valid():
# 			raise ValueError("Invalid form data")
# 		instance = FluidPropertiesCoolPropForm(**form.cleaned_data)
# 		columnNames, propsTable = instance.computeFluidProps()
		
		return render_to_response(self.template_name, locals(), 
				context_instance=RequestContext(self.request))		



def flowResistanceView(request):
	if request.method == 'POST':
		from smo.simple_flow.FlowResistance import Pipe
		postData = json.loads(request.body)
		action = postData['action']
		parameters = postData['parameters']
		if (action == 'getInputs'):
			pipe = Pipe()
			inputs = pipe.group2Json(Pipe.inputs)
			print json.dumps(inputs, indent=4)
			return JsonResponse({'inputs' : inputs})
		if (action == 'computePressureDrop'):
			pipe = Pipe()
			pipe.fieldValuesFromJson(parameters)
			pipe.computeGeometry()
			pipe.computeUpstreamState()
			pipe.computePressureDrop()
			results = pipe.group2Json(Pipe.results) 
			return JsonResponse({'results' : results})
		else:
			raise ValueError('Unknown action "{0}"'.format(action)) 
	else:
		return render_to_response('ThermoFluids/FlowResistance.html', locals(), 
				context_instance=RequestContext(request))
		
def testView(request):
	return render_to_response('ThermoFluids/TestView.html', context_instance=RequestContext(request))