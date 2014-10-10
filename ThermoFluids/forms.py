'''
Created on Sep 10, 2014

@author: nasko
'''

from django import forms
from ThermoFluids.models import FluidPropertiesCoolPropModel

class FluidPropertiesCoolPropForm(forms.ModelForm):
	class Meta:
		model = FluidPropertiesCoolPropModel
		exclude = []
		