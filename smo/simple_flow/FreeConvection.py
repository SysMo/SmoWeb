'''
Created on Nov 27, 2014

@author: Atanas Pavlov
'''
from smo.numerical_model.model import NumericalModel
from smo.numerical_model.fields import *
import numpy as np
from smo.smoflow3d.SimpleMaterials import Fluids
from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict
from django.contrib.messages.tests.urls import show

GeometryConfigurations = OrderedDict((
	('VP', 'vertical plane'),
	('IPT', 'inclined plane top'),
	('IPB', 'inclined plane bottom'),
	('HPT', 'horizontal plane top'),
	('HPB', 'horizontal plane bottom'),
	('VC', 'vertical cylinder'),
	('HC', 'horizontal cylinder'),
	('SPH', 'sphere'),
#	('Fin', 'finnedPipe'),
	('CCF', 'convection coefficient')
	))

PropTemperatureConf = OrderedDict((
	('MT', 'mean temperature'),
	('FT', 'fluid temperature')
	))

SurfaceShapes = OrderedDict((
	('RCT', 'rectangular'),
	('CIR', 'circular')
	))

class FreeConvection(NumericalModel):
	fluidName = Choices(Fluids, default = 'Nitrogen', label = 'fluid')	
	TFluid = Quantity('Temperature', default = (15, 'degC'), label = 'fluid temeprature')
	TWall = Quantity('Temperature', default = (50, 'degC'), label = 'wall temeprature')
	propT = Choices(PropTemperatureConf, label = 'compute props at')
	pressure = Quantity('Pressure', default = (1, 'bar'), label = 'fluid pressure') 
	geomConf = Choices(GeometryConfigurations, default = 'VP', label = 'configuration')
	surfaceShape = Choices(SurfaceShapes, default = 'RCT', label = 'surface shape',
						show = '(self.geomConf == "HPT") || (self.geomConf == "HPB")')
	thermalInputs = FieldGroup([fluidName, pressure, TFluid, TWall, propT, geomConf], label = 'Thermal') 
	
	width = Quantity('Length', default = (1, 'm'), label = 'width', 
			show = '(self.geomConf == "VP") || (self.geomConf == "HPT" && self.surfaceShape == "RCT") || (self.geomConf == "HPB" && self.surfaceShape == "RCT") || (self.geomConf == "IPT") || (self.geomConf == "IPB")')
	length = Quantity('Length', default = (1, 'm'), label = 'length', 
			show = '(self.geomConf == "HPT" && self.surfaceShape == "RCT") || (self.geomConf == "HPB" && self.surfaceShape == "RCT") || (self.geomConf == "HC")')
	height = Quantity('Length', default = (1, 'm'), label = 'height', 
			show = '(self.geomConf == "VP") || (self.geomConf == "VC") || (self.geomConf == "IPT") || (self.geomConf == "IPB")')
	diameter = Quantity('Length', default = (5, 'mm'), label = 'diameter', 
		show = '(self.geomConf == "VC") || (self.geomConf == "HC") || (self.geomConf == "SPH") || (self.geomConf == "HPT" && self.surfaceShape == "CIR") || (self.geomConf == "HPB" && self.surfaceShape == "CIR")')
	angle = Quantity('Angle', default = (45, 'deg'), label = 'angle to the vertical',
			show ='(self.geomConf == "IPT") || (self.geomConf == "IPB")')
	inputArea = Quantity('Area', default = (1, 'm**2'), label = 'surface area', show = 'self.geomConf == "CCF"')
	input_h = Quantity('HeatTransferCoefficient', label = 'convection coefficient', show = 'self.geomConf == "CCF"')
	geometryInputs = FieldGroup([surfaceShape, width, length, height, diameter,  angle, inputArea, input_h], label = 'Geometry')
	
	inputs = SuperGroup([thermalInputs, geometryInputs])
	###############
	Tfilm = Quantity('Temperature', default = (30, 'degC'), label = 'film temperature')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	rho = Quantity('Density', label = 'density')
	mu = Quantity('DynamicViscosity', label = 'dynamic viscosity')
	beta = Quantity('ThermalExpansionCoefficient', label = 'beta')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')
	fluidProps = FieldGroup([Tfilm, rho, cond, mu, beta, Pr], label = "Fluid propeties")

	deltaT = Quantity('TemperatureDifference', label = 'temperature difference')
	Gr = Quantity('Dimensionless', label = 'Grashof number')
	Ra = Quantity('Dimensionless', label = 'Rayleigh number')
	Nu = Quantity('Dimensionless', label = 'Nusselt number')
	h = Quantity('HeatTransferCoefficient', label = 'convection coefficient')
	area = Quantity('Area', label = 'surface area')
	QDot = Quantity('HeatFlowRate', label = 'heat flow rate')	
	heatExchangeResults = FieldGroup([deltaT, Gr, Ra, Nu, h, area, QDot], label = 'Heat exchange')
		
	results = SuperGroup([fluidProps, heatExchangeResults])
	
	def compute(self):
		self.deltaT = self.TWall - self.TFluid
		if (self.propT == 'MT'):
			self.Tfilm = (self.TWall + self.TFluid) / 2
		else:
			self.Tfilm = self.TFluid
		
		# Compute fluid properties
		fState = FluidState(self.fluidName)
		fState.update_Tp(self.Tfilm, self.pressure)		
		self.rho = fState.rho()
		self.mu = fState.mu()
		nu = self.mu / self.rho
		self.beta = fState.beta()
		self.Pr = fState.Pr()
		self.cond = fState.cond()
		
		# Compute geometry factors
		if (self.geomConf == 'VP'):
			s = self.height
			self.area = self.width * self.height
		elif (self.geomConf == 'HC'):
			s = self.diameter
			self.area = np.pi * self.diameter * self.length
		elif (self.geomConf == 'HPT' or self.geomConf == 'HPB'):
			if (self.surfaceShape == 'RCT'):
				s = self.width * self.length / (2.0 * (self.width + self.length))
				self.area = self.width * self.length
			elif (self.surfaceShape == 'CIR'):
				s = self.diameter / 4.0
				self.area = (np.pi / 4) * self.diameter ** 2
		elif (self.geomConf == 'SPH'):
			s = self.diameter
			self.area = np.pi * self.diameter ** 2
		elif (self.geomConf == 'IPT' or self.geomConf == 'IPB'):
			s = self.height
			self.area = self.width * self.height
		else:
			raise ValueError("Geometry configuration {0} not implemented".format(GeometryConfigurations[self.geomConf]))
		print s
		# Compute free convection dimensionless numbers
		self.Gr = 9.81 * (s ** 3) * self.beta * self.deltaT / (nu ** 2)
		self.Ra = self.Gr * self.Pr
		
		# Use the appropriate empirical Nusselt correlation
		if (self.geomConf == 'VP'):
			fPr = (1 + (0.492 / self.Pr) ** (9.0 / 16)) ** (-16.0 / 9)
			self.Nu = (0.825 + 0.387 * (self.Ra * fPr) ** (1.0 / 6)) ** 2			
		elif (self.geomConf == 'HC'):
			fPr = (1 + (0.559 / self.Pr) ** (9.0 / 16)) ** (-16.0 / 9)
			self.Nu = (0.6 + 0.387 * (self.Ra * fPr) ** (1.0 / 6)) ** 2			
		elif (self.geomConf == 'HPB'):
			fPr = (1 + (0.492 / self.Pr) ** (9.0 / 16)) ** (-16.0 / 9)
			if (self.Ra * fPr > 1e3 and self.Ra * fPr < 1e10):
				self.Nu = 0.6 * (self.Ra * fPr) ** (1.0 / 5)
			else: 
				raise ValueError("Unknown Nusselt correlation")
		elif (self.geomConf == 'HPT'):
			fPr = (1 + (0.322 / self.Pr) ** (11.0 / 20)) ** (-20.0 / 11) 
			if (self.Ra * fPr <= 7 * 1e4):
				self.Nu = 0.766 * (self.Ra * fPr) ** (1.0 / 5)
			else:
				self.Nu = 0.15 * (self.Ra * fPr) ** (1.0 / 3)
		elif (self.geomConf == 'SPH'):
			self.Nu = 0.56 * (self.Pr * self.Ra /(0.846 + self.Pr)) ** (1.0 / 4) + 2
		elif ((self.geomConf == 'IPT' and self.deltaT <= 0) or (self.geomConf == 'IPB' and self.deltaT >= 0)):
			fPr = (1 + (0.492 / self.Pr) ** (9.0 / 16)) ** (-16.0 / 9)
			self.Nu = (0.825 + 0.387 * (self.Ra * np.cos(self.angle) * fPr) ** (1.0 / 6)) ** 2	
		elif ((self.geomConf == 'IPT' and self.deltaT > 0) or (self.geomConf == 'IPB' and self.deltaT < 0)):
			Ra_crit = 10 ** (8.9 - 0.00178 * (self.angle * 180 / np.pi) ** 1.82)
			self.Nu = 0.56 * (Ra_crit * np.cos(self.angle)) ** (1.0 / 4) + 0.13 * (self.Ra ** (1.0 / 3) - Ra_crit ** (1.0 / 3))
		else: 
			pass
		
		# Compute the convection coefficient and the total heat flow rate
		self.h = self.Nu * self.cond / s
		self.QDot = self.area * self.h * self.deltaT
		
		
		
			
			
		
		
		
		