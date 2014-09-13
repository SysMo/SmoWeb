'''
Created on Sep 10, 2014

@author: nasko
'''

from django import forms
from SmoFluidProps.models import FluidProps_SetUpModel

class FluidProps_SetUpForm(forms.ModelForm):
	exclude = []
	class Meta:
		model = FluidProps_SetUpModel
		