from django.shortcuts import render
from django.views.generic import TemplateView
from SmoFluidProps.forms import FluidProps_SetUpForm
from SmoFluidProps.models import FluidProps_SetUpModel
from django.core.context_processors import csrf
# Create your views here.

class FluidProps_SetUpView(TemplateView):
	template_name = "SmoFluidProps/SetUp.html"
	def get(self, request, fluidPropsId = None):
		instance = FluidProps_SetUpModel()
		form = FluidProps_SetUpForm(instance = instance)
		context = self.get_context_data()
		context['form'] = form
		context['locals'] = {}
		return render(self.request, self.template_name, context)
	def post(self, request):
		form = FluidProps_SetUpForm(request.POST)
		if form.is_valid():
			pass
		else:
			raise ValueError("Invalid form data")
		instance = FluidProps_SetUpModel(**form.cleaned_data)
		columnNames, propsTable = instance.computeFluidProps()
		context = self.get_context_data()
		context['form'] = form
		context['locals'] = {'propsTable' : propsTable, 'columnNames' : columnNames}
		return render(self.request, self.template_name, context)		
		
	
	