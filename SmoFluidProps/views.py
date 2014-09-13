from django.shortcuts import render
from django.views.generic import TemplateView
from SmoFluidProps.forms import FluidProps_SetUpForm
from SmoFluidProps.models import FluidProps_SetUpModel
from django.core.context_processors import csrf
# Create your views here.

class FluidProps_SetUpView(TemplateView):
	template_name = "SmoFluidProps/SetUp.html"
	def get(self, request, fluidPropsId = None):
#		import uuid
#		id = uuid.uuid1().int
		instance = FluidProps_SetUpModel()
#		FluidProps_ObjectList[id] = instance
		form = FluidProps_SetUpForm(instance = instance)
		context = self.get_context_data()
#		context['id'] = id
		context['form'] = form
		context['locals'] = {}
		return render(self.request, self.template_name, context)
	def post(self, request):
		form = FluidProps_SetUpForm(request.POST)
		if form.is_valid():
			print form.cleaned_data
		else:
			raise ValueError("Invalid form data")

		instance = FluidProps_SetUpModel(**form.cleaned_data)
# 		for field in instance._meta.fields:
# 			if (field.name != 'id'):
# 				print(field.name)
# 				print(field.name, request.POST[field.name])
# 				instance.__setattr__(field.name, request.POST[field.name])

		
		columnNames, propsTable = instance.computeFluidProps()
		
		context = self.get_context_data()
		context['form'] = form
		context['locals'] = {'propsTable' : propsTable, 'columnNames' : columnNames}
		#print propsTable

		return render(self.request, self.template_name, context)		
		
	
	