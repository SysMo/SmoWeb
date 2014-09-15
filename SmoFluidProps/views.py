from django.shortcuts import render_to_response, RequestContext
from django.views.generic import TemplateView
from SmoFluidProps.forms import FluidProps_SetUpForm
from SmoFluidProps.models import FluidProps_SetUpModel
from django.core.context_processors import csrf
# Create your views here.

class FluidProps_SetUpView(TemplateView):
	template_name = "SmoFluidProps/SetUp.html"
	def get(self, request):
		form = FluidProps_SetUpForm()
		
		return render_to_response(self.template_name, locals(), 
								context_instance=RequestContext(self.request))
	def post(self, request):
		form = FluidProps_SetUpForm(self.request.POST)
		if not form.is_valid():
			raise ValueError("Invalid form data")
		instance = FluidProps_SetUpModel(**form.cleaned_data)
		columnNames, propsTable = instance.computeFluidProps()
		
		return render_to_response(self.template_name, locals(), 
								context_instance=RequestContext(self.request))		
		
	
	