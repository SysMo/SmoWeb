'''
Created on Nov 27, 2014

@author: Atanas Pavlov
'''
from smo.model.model import NumericalModel, ModelView, ModelDocumentation
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
import numpy as np
from smo.media.SimpleMaterials import Fluids
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from collections import OrderedDict

GeometryConfigurationsExternal = OrderedDict((
	('VP', 'vertical plane'),
	('IPT', 'inclined plane top'),
	('IPB', 'inclined plane bottom'),
	('HPT', 'horizontal plane top'),
	('HPB', 'horizontal plane bottom'),
	('VC', 'vertical cylinder'),
	('HC', 'horizontal cylinder'),
	('SPH', 'sphere'),
	('FIN', 'finned pipe'),
	('CCF', 'convection coefficient'),
	))

GeometryConfigurationsInternal = OrderedDict((
	('HP', 'horizontal planes'),
	('VP', 'vertical planes'),
	('IP', 'inclined planes'),
	('HA', 'horizontal annuli'),
	))

PropTemperatureConf = OrderedDict((
	('MT', 'mean temperature'),
	('FT', 'fluid temperature')
	))

SurfaceShapes = OrderedDict((
	('RCT', 'rectangular'),
	('CIR', 'circular')
	))

class FreeConvection_External(NumericalModel):
	name = "FreeConvection_External"
	label = "Free Convection External"
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'Nitrogen', label = 'fluid')	
	TFluid = Quantity('Temperature', default = (15, 'degC'), label = 'fluid temeprature')
	TWall = Quantity('Temperature', default = (50, 'degC'), label = 'wall temeprature')
	propT = Choices(PropTemperatureConf, label = 'compute props at')
	pressure = Quantity('Pressure', default = (1, 'bar'), label = 'fluid pressure') 
	geomConf = Choices(GeometryConfigurationsExternal, default = 'VP', label = 'configuration')
	surfaceShape = Choices(SurfaceShapes, default = 'RCT', label = 'surface shape',
						show = '(self.geomConf == "HPT") || (self.geomConf == "HPB")')
	heatExchangeGain = Quantity('Dimensionless', label = 'heat exchange gain')
	thermalInputs = FieldGroup([fluidName, pressure, TFluid, TWall, propT, geomConf, heatExchangeGain], label = 'Thermal') 
	#####
	width = Quantity('Length', default = (1, 'm'), label = 'width', 
			show = '(self.geomConf == "VP") || (self.geomConf == "HPT" && self.surfaceShape == "RCT") || (self.geomConf == "HPB" && self.surfaceShape == "RCT") || (self.geomConf == "IPT") || (self.geomConf == "IPB")')
	length = Quantity('Length', default = (1, 'm'), label = 'length', 
			show = '(self.geomConf == "HPT" && self.surfaceShape == "RCT") || (self.geomConf == "HPB" && self.surfaceShape == "RCT")\
				|| (self.geomConf == "IPT") || (self.geomConf == "IPB") || (self.geomConf == "HC") || (self.geomConf == "FIN")')
	height = Quantity('Length', default = (1, 'm'), label = 'height', 
			show = '(self.geomConf == "VP") || (self.geomConf == "VC")')
	diameter = Quantity('Length', default = (5, 'mm'), label = 'diameter', 
		show = '(self.geomConf == "VC") || (self.geomConf == "HC") || (self.geomConf == "SPH") || (self.geomConf == "HPT" && self.surfaceShape == "CIR") || (self.geomConf == "HPB" && self.surfaceShape == "CIR") || (self.geomConf == "FIN")')
	angle = Quantity('Angle', default = (45, 'deg'), maxValue = (90, 'deg'), label = 'angle to the vertical',
			show ='(self.geomConf == "IPT") || (self.geomConf == "IPB")')
	finSpacing = Quantity('Length', default = (0.020, 'm'), label = 'fin spacing', 
			show = '(self.geomConf == "FIN")')
	finThickness = Quantity('Length', default = (0.002, 'm'), label = 'fin thickness', 
			show = '(self.geomConf == "FIN")')
	finHeight = Quantity('Length', default = (0.03, 'm'), label = 'fin height', 
			show = '(self.geomConf == "FIN")')
	inputArea = Quantity('Area', default = (1, 'm**2'), label = 'surface area', show = 'self.geomConf == "CCF"')
	input_alpha = Quantity('HeatTransferCoefficient', label = 'convection coefficient', show = 'self.geomConf == "CCF"')
	geometryInputs = FieldGroup([surfaceShape, width, length, height, diameter,  angle, inputArea, input_alpha, 
								finHeight, finThickness, finSpacing], label = 'Geometry')
	
	inputs = SuperGroup([thermalInputs, geometryInputs])
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	Tfilm = Quantity('Temperature', default = (30, 'degC'), label = 'film temperature')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	rho = Quantity('Density', label = 'density')
	mu = Quantity('DynamicViscosity', label = 'dynamic viscosity')
	beta = Quantity('ThermalExpansionCoefficient', label = 'beta')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')
	fluidProps = FieldGroup([Tfilm, rho, cond, mu, beta, Pr], label = "Fluid propeties")
	#####
	deltaT = Quantity('TemperatureDifference', label = 'temperature difference')
	Gr = Quantity('Dimensionless', label = 'Grashof number')
	Ra = Quantity('Dimensionless', label = 'Rayleigh number')
	Nu = Quantity('Dimensionless', label = 'Nusselt number')
	alpha = Quantity('HeatTransferCoefficient', label = 'convection coefficient')
	area = Quantity('Area', label = 'surface area')
	QDot = Quantity('HeatFlowRate', label = 'heat flow rate')	
	heatExchangeResults = FieldGroup([deltaT, Gr, Ra, Nu, alpha, area, QDot], label = 'Heat exchange')
		
	results = SuperGroup([fluidProps, heatExchangeResults])
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]

	############# Methods ###############	
	def compute(self):
		self.deltaT = self.TWall - self.TFluid
		if (self.propT == 'MT'):
			self.Tfilm = (self.TWall + self.TFluid) / 2.0
		else:
			self.Tfilm = self.TFluid
		
		# Compute fluid properties
		fState = FluidState(self.fluidName)
		fState.update_Tp(self.Tfilm, self.pressure)		
		self.rho = fState.rho
		self.mu = fState.mu
		nu = self.mu / self.rho
		self.beta = fState.beta
		self.Pr = fState.Pr
		self.cond = fState.cond
		
		# Compute geometry factors
		if (self.geomConf == 'VP'):
			s = self.height
			self.area = self.width * self.height
		elif (self.geomConf == 'VC'):
			s = self.height
			self.area = np.pi * self.diameter * self.height
		elif (self.geomConf == 'HC'):
			s = self.diameter
			self.area = np.pi * self.diameter * self.length
		elif (self.geomConf == 'HPT' or self.geomConf == 'HPB'):
			if (self.surfaceShape == 'RCT'):
				s = self.width * self.length / (2.0 * (self.width + self.length))
				self.area = self.width * self.length
			elif (self.surfaceShape == 'CIR'):
				s = self.diameter / 4.0
				self.area = (np.pi / 4) * self.diameter**2
		elif (self.geomConf == 'SPH'):
			s = self.diameter
			self.area = np.pi * self.diameter**2
		elif (self.geomConf == 'IPT' or self.geomConf == 'IPB'):
			s = self.length
			self.area = self.width * self.height
		elif (self.geomConf == 'FIN'):
			#halfway between full rib and bare pipe
			s = self.diameter + self.finHeight;
			finsPerLength = 1.0/(self.finThickness + self.finSpacing)
			self.area = np.pi * self.diameter * (1 - self.finThickness * finsPerLength)
			self.area += finsPerLength * np.pi * self.finHeight * 2 * (self.diameter + self.finHeight)
			self.area += finsPerLength * np.pi * self.finThickness * (self.diameter + 2 * self.finHeight)
			self.area *= self.length
		else:
			raise ValueError("Geometry configuration {0} not implemented".format(GeometryConfigurationsExternal[self.geomConf]))
		
		# Compute free convection dimensionless numbers
		self.Gr = 9.81 * (s**3) * self.beta * np.abs(self.deltaT) / (nu**2)
		self.Ra = self.Gr * self.Pr
		
		# Use the appropriate empirical Nusselt correlation
		if (self.geomConf == 'VP'):
			fPr = (1 + (0.492 / self.Pr)**(9.0 / 16))**(-16.0 / 9)
			self.Nu = (0.825 + 0.387 * (self.Ra * fPr)**(1.0 / 6))**2
		elif (self.geomConf == 'VC'):
			fPr = (1 + (0.492 / self.Pr)**(9.0 / 16))**(-16.0 / 9)
			Nu_plate = (0.825 + 0.387 * (self.Ra * fPr)**(1.0 / 6))**2
			self.Nu = Nu_plate + 0.97 * self.height / self.diameter		
		elif (self.geomConf == 'HC'):
			fPr = (1 + (0.559 / self.Pr)**(9.0 / 16))**(-16.0 / 9)
			self.Nu = (0.6 + 0.387 * (self.Ra * fPr)**(1.0 / 6))**2			
		elif ((self.geomConf == 'HPT' and self.deltaT <= 0) or (self.geomConf == 'HPB' and self.deltaT >= 0)):
			fPr = (1 + (0.492 / self.Pr)**(9.0 / 16))**(-16.0 / 9)
			if (self.Ra * fPr < 1e10):
				self.Nu = 0.6 * (self.Ra * fPr)**(1.0 / 5)
				if (self.Nu < 1):
					self.Nu = 1
			else: 
				raise ValueError("Outside range of validity")
		elif ((self.geomConf == 'HPT' and self.deltaT > 0) or (self.geomConf == 'HPB' and self.deltaT < 0)):
			fPr = (1 + (0.322 / self.Pr)**(11.0 / 20))**(-20.0 / 11) 
			if (self.Ra * fPr <= 7 * 1e4):
				self.Nu = 0.766 * (self.Ra * fPr)**(1.0 / 5)
			else:
				self.Nu = 0.15 * (self.Ra * fPr)**(1.0 / 3)
		elif (self.geomConf == 'SPH'):
			self.Nu = 0.56 * (self.Pr * self.Ra /(0.846 + self.Pr))**(1.0 / 4) + 2
		elif ((self.geomConf == 'IPT' and self.deltaT <= 0) or (self.geomConf == 'IPB' and self.deltaT >= 0)):
			fPr = (1 + (0.492 / self.Pr)**(9.0 / 16))**(-16.0 / 9)
			self.Nu = (0.825 + 0.387 * (self.Ra * np.cos(self.angle) * fPr)**(1.0 / 6))**2	
		elif ((self.geomConf == 'IPT' and self.deltaT > 0) or (self.geomConf == 'IPB' and self.deltaT < 0)):
			Ra_crit = 10**(8.9 - 0.00178 * (self.angle * 180 / np.pi)**1.82)
			self.Nu = 0.56 * (Ra_crit * np.cos(self.angle))**(1.0 / 4) + 0.13 * (self.Ra**(1.0 / 3) - Ra_crit**(1.0 / 3))
		elif (self.geomConf == 'FIN'):
			#Correlation from VDI Heat Atlas F2.4.4
			self.Nu = 0.24 * (self.Ra * self.finSpacing / self.diameter)**(1.0 / 3)
		else: 
			pass
		self.Nu = self.Nu * self.heatExchangeGain
		
		# Compute the convection coefficient and the total heat flow rate
		self.alpha = self.Nu * self.cond / s
		self.QDot = self.area * self.alpha * self.deltaT

class FreeConvection_Internal(NumericalModel):
	name = "FreeConvection_Internal"
	label = "Free Convection Internal"
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'Nitrogen', label = 'fluid')	
	geomConf = Choices(GeometryConfigurationsInternal, default = 'HP', label = 'configuration')
	TWallTop = Quantity('Temperature', default = (50, 'degC'), label = 'temeprature top',
					show = '(self.geomConf == "HP") || (self.geomConf == "IP")')
	TWallBottom = Quantity('Temperature', default = (50, 'degC'), label = 'temeprature bottom',
					show = '(self.geomConf == "HP") || (self.geomConf == "IP")')
	TWallLeft = Quantity('Temperature', default = (50, 'degC'), label = 'temeprature left',
					show = '(self.geomConf == "VP")')
	TWallRight = Quantity('Temperature', default = (50, 'degC'), label = 'temeprature right',
					show = '(self.geomConf == "VP")')
	TInner = Quantity('Temperature', default = (50, 'degC'), label = 'temeprature inner',
					show = '(self.geomConf == "HA")')
	TOuter = Quantity('Temperature', default = (50, 'degC'), label = 'temeprature outer',
					show = '(self.geomConf == "HA")')
	pressure = Quantity('Pressure', default = (1, 'bar'), label = 'fluid pressure') 
	heatExchangeGain = Quantity('Dimensionless', label = 'heat exchange gain')
	thermalInputs = FieldGroup([fluidName, pressure, TWallTop, TWallBottom, TWallLeft, TWallRight, TInner, TOuter, geomConf, heatExchangeGain], label = 'Thermal') 
	#####
	width = Quantity('Length', default = (1, 'm'), label = 'width',
					show = '(self.geomConf == "HP") || (self.geomConf == "VP") || (self.geomConf == "IP")')
	length = Quantity('Length', default = (1, 'm'), label = 'length',
					show = '(self.geomConf == "HP") || (self.geomConf == "IP") || (self.geomConf == "HA")')
	height = Quantity('Length', default = (1, 'm'), label = 'height',
					show = '(self.geomConf == "VP")')
	dist = Quantity('Length', default = (1, 'm'), label = 'distance b/n planes',
					show = '(self.geomConf == "HP") || (self.geomConf == "VP") || (self.geomConf == "IP")')	
	rInner = Quantity('Length', default = (1, 'm'), label = 'radius inner',
					show = '(self.geomConf == "HA")')
	rOuter = Quantity('Length', default = (1, 'm'), label = 'radius outer',
					show = '(self.geomConf == "HA")')	
	angle = Quantity('Angle', default = (45, 'deg'), maxValue = (90, 'deg'), label = 'angle to the vertical',
			show ='(self.geomConf == "IP")')
	
	geometryInputs = FieldGroup([width, length, height, dist, rInner, rOuter, angle], label = 'Geometry')
	
	inputs = SuperGroup([thermalInputs, geometryInputs])
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	Tfilm = Quantity('Temperature', default = (30, 'degC'), label = 'film temperature')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	rho = Quantity('Density', label = 'density')
	mu = Quantity('DynamicViscosity', label = 'dynamic viscosity')
	beta = Quantity('ThermalExpansionCoefficient', label = 'beta')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')
	fluidProps = FieldGroup([Tfilm, rho, cond, mu, beta, Pr], label = "Fluid propeties")
	#####
	deltaT = Quantity('TemperatureDifference', label = 'temperature difference')
	Gr = Quantity('Dimensionless', label = 'Grashof number')
	Ra = Quantity('Dimensionless', label = 'Rayleigh number')
	Nu = Quantity('Dimensionless', label = 'Nusselt number')
	alpha = Quantity('HeatTransferCoefficient', label = 'convection coefficient')
	area = Quantity('Area', label = 'surface area')
	QDot = Quantity('HeatFlowRate', label = 'heat flow rate')	
	heatExchangeResults = FieldGroup([deltaT, Gr, Ra, Nu, alpha, area, QDot], label = 'Heat exchange')
		
	results = SuperGroup([fluidProps, heatExchangeResults])
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]

	############# Methods ###############	
	def compute(self):
		if (self.geomConf == 'HP' or self.geomConf == 'IP'):
			self.Tfilm = (self.TWallTop + self.TWallBottom) / 2.0
			self.deltaT = self.TWallTop - self.TWallBottom
		elif (self.geomConf == 'VP'):
			self.Tfilm = (self.TWallLeft + self.TWallRight) / 2.0
			self.deltaT = self.TWallLeft - self.TWallRight
		elif (self.geomConf == 'HA'):
			self.Tfilm = (self.TInner + self.TOuter) / 2.0
			self.deltaT = self.TInner - self.TOuter
		
		# Compute fluid properties
		fState = FluidState(self.fluidName)
		fState.update_Tp(self.Tfilm, self.pressure)		
		self.rho = fState.rho
		self.mu = fState.mu
		nu = self.mu / self.rho
		self.beta = fState.beta
		self.Pr = fState.Pr
		self.cond = fState.cond
			
		# Compute geometry factors
		if (self.geomConf == 'HP' or self.geomConf == 'IP'):
			s = self.dist
			self.area = self.width * self.length
		elif (self.geomConf == 'VP'):
			s = self.dist
			self.area = self.width * self.height
		elif (self.geomConf == 'HA'):
			s = self.rOuter - self.rInner
			self.area = 2 * np.pi * self.rInner * self.length
		else:
			raise ValueError("Geometry configuration {0} not implemented".format(GeometryConfigurationsInternal[self.geomConf]))
		
		# Compute free convection dimensionless numbers
		self.Gr = 9.81 * (s**3) * self.beta * np.abs(self.deltaT) / (nu**2)
		self.Ra = self.Gr * self.Pr
		
		# Use the appropriate empirical Nusselt correlation
		if (self.geomConf == 'HP'):
			if (self.Ra >= 0 and self.Ra <= 1708):
				self.Nu = 1.
			elif (self.Ra > 1708 and self.Ra <= 2.2 * 1e4):
				self.Nu = 0.208 * self.Ra**0.25
			elif (self.Ra > 2.2 * 1e4):
				self.Nu = 0.092 * self.Ra**0.33
		elif (self.geomConf == 'VP'):
			if (self.height / s <= 80):
				if (self.Ra > 1e9):
					raise ValueError("Outside range of validity")
				else:
					if (self.Ra > 1e7):
						self.Nu = 0.049 * self.Ra**0.33
					else:
						self.Nu = 0.42 * self.Pr**0.012 * self.Ra**0.25 * (self.height / s)**(-0.25)
						if (self.Nu < 1.):
							self.Nu = 1.				
			else:
				raise ValueError("Outside range of validity")
		elif (self.geomConf == 'IP'):
			if (self.deltaT < 0):
				from scipy.interpolate import interp1d
				angles = np.array([0, 30, 45, 60, 90])
				values = np.array([4.9, 5.7, 5.9, 6.5, 6.9]) * 1e-2
				interpFunc = interp1d(angles, values, kind='linear')
				C =  interpFunc(self.angle)
				self.Nu = C * self.Ra**0.33 * self.Pr**0.074
			else:
				if (self.Ra >= 5e3 and self.Ra <= 1e8):
					if (self.angle == 45):
						self.Nu = 1 + (0.025 * self.Ra**1.36) / (self.Ra + 1.3 + 1e4)
					else:
						raise ValueError("Outside range of validity")
				else:
					raise ValueError("Outside range of validity")
		elif (self.geomConf == 'HA'):
			if (self.deltaT > 0):
				if (self.Ra > 7.1e3):
					if (self.rOuter / self.rInner) <= 8:
						self.Nu = 0.2 * self.Ra**0.25 * (self.rOuter / self.rInner)**0.5
					else:
						raise ValueError("Outside range of validity")
				else:
					raise ValueError("Outside range of validity")
			else:
				raise ValueError("Outside range of validity")
		else: 
			pass
		self.Nu = self.Nu * self.heatExchangeGain
		
		# Compute the convection coefficient and the total heat flow rate
		self.alpha = self.Nu * self.cond / s
		self.QDot = self.area * self.alpha * self.deltaT

class FreeConvectionDoc(ModelDocumentation):
	name = 'FreeConvectionDoc'
	label = 'Free Convection (Docs)'
	template = 'documentation/html/FreeConvectionDoc.html'	