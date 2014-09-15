from django.db import models

# Create your models here.


class FluidProps_SetUpModel(models.Model):	
	STATE_VARIABLE_CHOICES = (
		('PT', 'pressure & temperature'),
		('PH', 'pressure & enthalpy'),
		('PS', 'pressure & entropy'),
		('PQ', 'pressure & vapor quality'),
		('TQ', 'temperature & vapor quality')
	)
	fluidName = models.CharField("Fluid name", max_length = 50, default = 'ParaHydrogen')
	stateVariables = models.CharField(
		max_length = '2', default = 'PT',
		choices = STATE_VARIABLE_CHOICES
	)
	stateVariable1MinValue = models.FloatField("Min value", default = 30)
	stateVariable1MaxValue = models.FloatField("Max value", default = 300)
	stateVariable1NumValues = models.IntegerField("Num values", default = 10)
	
	stateVariable2Value = models.FloatField("Value", default = 30)
	########################
	
	
	def computeFluidProps(self):
		from smo.Media import MediumState, Medium
		import numpy as np
		state1Values = np.linspace(
			self.stateVariable1MinValue, self.stateVariable1MaxValue, 
			self.stateVariable1NumValues, True)
		rowDType = np.dtype([
				('p', np.float), ('T', np.float),
				('rho', np.float), ('h', np.float),
				
				])
		#'s', 'u', 'cp', 'cv', 'dpdt_v', 'dpdv_t', 'dvdt_p', 'beta', 'mu', 'cond', 'Pr', 'gamma' 
		columnNames = ['Pressure', 'Temperature', 'Density', 'Spec. Enthalpy', 
					'Internal Energy', 'Spec. Heat Capacity cp', 'Spec. Heat Capacity cv', 
					'(dp/dt)_v', '(dp/dv)_t', '(dv/dt)_p', 'beta', 
					'Dyn. viscosity', 'Thermal conductivity', 'Prandtl', 'Gamma']
		tableValues = np.zeros(
			(self.stateVariable1NumValues, len(columnNames)), dtype = float)
		
		if (self.fluidName in RegisteredFluids.keys()):			
			fluid = RegisteredFluids[self.fluidName]
		else:
			fluid = Medium.create(Medium.sCompressibleFluidCoolProp,
				 self.fluidName, len(RegisteredFluids))
			RegisteredFluids[self.fluidName] = fluid
			
		for i in range(self.stateVariable1NumValues):
			fp = MediumState(fluid)
			fp.update_Tp(state1Values[i], self.stateVariable2Value)
			tableValues[i] = (
					fp.p(), fp.T(), fp.rho(), fp.h(),
					fp.u(), fp.cp(), fp.cv(), 
					fp.dpdt_v(), fp.dpdv_t(), fp.dvdt_p(), fp.beta(),
					fp.mu(), fp.cond(), fp.Pr(), fp.gamma(), 
				)
			#tableValues[i]['T'] = fp.T()
			#tableValues[i]['rho'] = fp.rho()
			#tableValues[i]['h'] = fp.h()
		return columnNames, tableValues
	
RegisteredFluids = {}