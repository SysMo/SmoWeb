from django.shortcuts import render_to_response, RequestContext
from django.views.generic import TemplateView
from ThermoFluids.forms import FluidPropertiesCoolPropForm
from django.core.context_processors import csrf
# Create your views here.

class FluidPropertiesCoolPropView(TemplateView):
	template_name = "ThermoFluids/FluidPropertiesCoolProp.html"
	def get(self, request):
		form = FluidPropertiesCoolPropForm()
		
		return render_to_response(self.template_name, locals(), 
				context_instance=RequestContext(self.request))
		
	def post(self, request):
		form = FluidPropertiesCoolPropForm(self.request.POST)
		if not form.is_valid():
			raise ValueError("Invalid form data")
		instance = FluidPropertiesCoolPropForm(**form.cleaned_data)
		columnNames, propsTable = instance.computeFluidProps()
		
		return render_to_response(self.template_name, locals(), 
				context_instance=RequestContext(self.request))		
		
def testView(request):
	return render_to_response('ThermoFluids/TestView.html', context_instance=RequestContext(request))