'''
Created on Dec 15, 2014

@author: Atanas Pavlov
'''
import numpy as np
from smo.model.model import NumericalModel
from smo.model.fields import *
from smo.media.SimpleMaterials import Solids
from collections import OrderedDict

class WireHeatingSolver(object):
	pass

BoundaryConditionChoice = OrderedDict((
	('T', 'temperature'),
	('Q', 'heat flux')	
	))

class WireHeating1D(NumericalModel):
	d = Quantity('Length', default = (2, 'mm'), label = 'diameter')
	L = Quantity('Length', default = (1, 'm'), label = 'length')
	n = Quantity('Dimensionless', default = 50, maxValue=200, label = 'num. elements')
	thermalCond = Quantity('ThermalConductivity', default = 401, label = 'thermal conductivity')
	eCond = Quantity('ElectricalConductivity', default = 5.96e7, label = 'electrical conductivity')
	I = Quantity('ElectricalCurrent', default = (10, 'A'), label = 'electrical current')
	g1 = FieldGroup([d, L, n, thermalCond, eCond, I], label = 'Wire')
	
	bcLeft = Choices(BoundaryConditionChoice, label='boundary condition (left)')
	TLeftInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeftInput = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	bcRight = Choices(BoundaryConditionChoice, label='boundary condition (right)')
	TRightInput = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRightInput = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	h = Quantity('HeatTransferCoefficient', default = (10, 'W/m**2-K'), label = 'convection coefficient')	
	g2 = FieldGroup([bcLeft, TLeftInput, QLeftInput, bcRight, TRightInput, QRightInput, h], label = 'Boundary conditions')
	
	inputs = SuperGroup([g1, g2]) 
	#####################
	Acs = Quantity('Area', default = (1, 'mm**2'), label = 'cross sectional area')
	As = Quantity('Area', default = (1, 'mm**2'), label = 'surface area')
	r1 = FieldGroup([Acs, As], label = 'Res') 
	
	TLeft = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (left)', show = 'self.bcLeft == "T"')
	QLeft = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (left)', show = 'self.bcLeft == "Q"')
	TRight = Quantity('Temperature', default = (20, 'degC'), label = 'temperature (right)', show = 'self.bcRight == "T"')
	QRight = Quantity('HeatFlowRate', default = (0, 'W'), label = 'heat flow (right)', show = 'self.bcRight == "Q"')
	
	results = SuperGroup([r1])
	
	def compute(self):
		self.Acs = np.pi/4 * self.d * self.d
		self.As = np.pi * self.d * self.L
		
		# Create the thermal model object
		model = WireHeatingSolver()
		# Create mesh
		model.createLinearMesh(L = self.L, d = self.d, n = self.n)
		# Set boundary conditions
		if (self.bcLeft == 'T'):
			model.setBoundaryConditions(0, 'T', self.TLeftInput)
		else:
			model.setBoundaryConditions(0, 'Q', self.QLeftInput)
		
		if (self.bcRight == 'T'):
			model.setBoundaryConditions(1, 'T', self.TRightInput)
		else:
			model.setBoundaryConditions(1, 'Q', self.QRightInput)
			
# model = CryogenicPipeSolver()
# model.thermalCond = Copper.thermalCond
# model.createLinearMesh(L = 1, d = 1.784e-3, n = 30)
# #model.thermalCond = POM.thermalCond
# #model.createRadialMesh(rMin = 0.005, rMax = 0.2, width = 3.0e-3, n = 50)
# model.setBoundaryConditions(0, 'T', 80)
# model.setBoundaryConditions(1, 'T', 20)
# model.h = 5
# model.solve()
# print model.heatFluxes[0][0]
# model.plotTemperature()