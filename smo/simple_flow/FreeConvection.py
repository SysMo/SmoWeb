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
	conf = Choices(ConvectionConfigurations, default = 'Vert', label = 'configuration')
	thermal = FieldGroup([fluidName, TFluid, TWall, useTFilm, conf], label = 'Thermal') 
	
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
	area = Quantity('Area', default = (1, 'm**2'), label = 'surface area', show = 'self.conf == "ConvCoeff"')
	h = Quantity('HeatTransferCoefficient', label = 'convection coefficient', show = 'self.conf == "ConvCoeff"')
	geometry = FieldGroup([width, length, height, diameter,  angle, area, h], label = 'Geometry')
	
	inputs = SuperGroup([thermal, geometry])
	###############
	deltaT = Quantity('TemperatureDifference', label = 'temperature difference')
	Tfilm = Quantity('Temperature', default = (30, 'degC'), label = 'film temperature')
	Gr = Quantity('Dimensionless', label = 'Grashof number')
	Ra = Quantity('Dimensionless', label = 'Rayleigh number')
	Nu = Quantity('Dimensionless', label = 'Nusselt number')
	QDot = Quantity('HeatFlowRate', label = 'heat flow rate')
	
	def compute(self):
		self.deltaT = self.TWall - self.TFluid
		self.Tfilm = (self.TWall - self.TFluid) / 2
		if (self.useTFilm):
			TConv = self.Tfilm
		else:
			TConv = self.TFluid
		fluid = FluidState(self.fluidName)
		