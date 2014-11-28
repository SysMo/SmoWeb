'''
Created on Nov 27, 2014

@author: Atanas Pavlov
'''
from smo.numerical_model.model import NumericalModel
from smo.numerical_model.fields import *
import numpy
from smo.smoflow3d.SimpleMaterials import Fluids
from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict
from django.contrib.messages.tests.urls import show

ConvectionConfigurations = OrderedDict((
	('Vert', 'vertical plane'),
	('Incl', 'inclined plane'),
	('HorizTop', 'horizontal plane top'),
	('HorizBottom', 'horizontal plane bottom'),
	('VertCyl', 'vertical cylinder'),
	('HorizCyl', 'horizontal cylinder'),
	('Sphere', 'sphere'),
#	('Fin', 'finnedPipe'),
	('ConvCoeff', 'convection coefficient')
	))

class FreeConvection(NumericalModel):
	fluidName = Choices(Fluids, default = 'Nitrogen', label = 'fluid')	
	TFluid = Quantity('Temperature', default = (15, 'degC'), label = 'fluid temeprature')
	TWall = Quantity('Temperature', default = (50, 'degC'), label = 'wall temeprature')
	useTFilm = Boolean(default = 'True', label = 'use film temperature')
	pressure = Quantity('Pressure', default = (1, 'bar'), label = 'fluid pressure') 
	conf = Choices(ConvectionConfigurations, default = 'Vert', label = 'configuration')
	thermalInputs = FieldGroup([fluidName, TFluid, TWall, useTFilm, conf], label = 'Thermal') 
	
	width = Quantity('Length', default = (1, 'm'), label = 'width', 
			show = '(self.conf == "Vert") || (self.conf == "Incl") || (self.conf == "HorizTop") || (self.conf == "HorizBottom")')
	length = Quantity('Length', default = (1, 'm'), label = 'length', 
			show = '(self.conf == "Incl") || (self.conf == "HorizTop") || (self.conf == "HorizBottom") || (self.conf == "HorizCyl")')
	height = Quantity('Length', default = (1, 'm'), label = 'height', 
			show = '(self.conf == "Vert") || (self.conf == "VertCyl")')
	diameter = Quantity('Length', default = (5, 'mm'), label = 'diameter', 
		show = '(self.conf == "VertCyl") || (self.conf == "HorizCyl") || (self.conf == "Sphere")')
	angle = Quantity('Angle', default = (45, 'deg'), label = 'inclination',
			show ='self.conf == "Incl"')
	inputArea = Quantity('Area', default = (1, 'm**2'), label = 'surface area', show = 'self.conf == "ConvCoeff"')
	input_h = Quantity('HeatTransferCoefficient', label = 'convection coefficient', show = 'self.conf == "ConvCoeff"')
	geometryInputs = FieldGroup([width, length, height, diameter,  angle, inputArea, input_h], label = 'Geometry')
	
	inputs = SuperGroup([thermalInputs, geometryInputs])
	###############
	deltaT = Quantity('TemperatureDifference', label = 'temperature difference')
	Tfilm = Quantity('Temperature', default = (30, 'degC'), label = 'film temperature')
	Gr = Quantity('Dimensionless', label = 'Grashof number')
	Ra = Quantity('Dimensionless', label = 'Rayleigh number')
	Nu = Quantity('Dimensionless', label = 'Nusselt number')
	QDot = Quantity('HeatFlowRate', label = 'heat flow rate')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	rho = Quantity('Density', label = 'density')
	mu = Quantity('DynamicViscosity', label = 'dynamic viscosity')
	h = Quantity('HeatTransferCoefficient', label = 'convection coefficient')
	beta = Quantity('Dimensionless', label = 'beta')
	thermalResults = FieldGroup([deltaT, Tfilm, Gr, Pr, Ra, Nu, QDot, h, cond, rho, mu, beta], label = 'Thermal')
	
	area = Quantity('Area', label = 'surface area')
	geometryResults = FieldGroup([area], label = 'Geometry')
	
	results = SuperGroup([thermalResults, geometryResults])
	
	def compute(self):
		self.deltaT = self.TWall - self.TFluid
		self.Tfilm = (self.TWall + self.TFluid) / 2
		if (self.useTFilm):
			TConv = self.Tfilm
		else:
			TConv = self.TFluid
		
		fState = FluidState(self.fluidName)
		fState.update_Tp(TConv, self.pressure)
		
		self.rho = fState.rho()
		self.mu = fState.mu()
		nu = self.mu / self.rho
		self.beta = fState.beta()
		self.Pr = fState.Pr()
		self.cond = fState.cond()
		
		if (self.conf == 'Vert'):
			s = self.height
		else:
			pass
		self.Gr = 9.81 * (s ** 3) * self.beta * self.deltaT / (nu ** 2)
		self.Ra = self.Gr * self.Pr
		
		if (self.conf == 'Vert'):
			fPr = (1 + (0.492 / self.Pr) ** (9.0 / 16)) ** (-16.0 / 9)
			self.Nu = (0.825 + 0.387 * (self.Ra * fPr) ** (1.0 / 6)) ** 2			
			self.area = self.width * self.height
			self.h = self.Nu * self.cond / s
			self.QDot = self.area * self.h * self.deltaT
		else: 
			pass
		
		
		
		
			
			
		
		
		
		