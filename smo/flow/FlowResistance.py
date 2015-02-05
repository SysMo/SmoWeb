import numpy as np
try:
	import pylab as plt
except Exception: 
	pass
import scipy.interpolate
import math
from smo.media.CoolProp.CoolProp import FluidState
from smo.model.model import NumericalModel, ModelView, RestBlock, HtmlBlock, ModelFigure, ModelDescription
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.MaterialData import Solids, Fluids
import json

class PipeFlow(NumericalModel):
	name = "PipeFlow"
	label = "Pipe Flow"
	figure = ModelFigure(src="ThermoFluids/img/StraightPipe.svg")
# 	description = ModelDescription('Pipe flow.', show = False)
	
	############# Inputs ###############
	# Fields
	internalDiameter = Quantity('Length', default = (5, 'mm'), label = 'internal diameter (d<sub>i</sub>)')
	externalDiameter = Quantity('Length', default = (6, 'mm'), label = 'external diameter (d<sub>e</sub>)')
	length = Quantity('Length', default = (1, 'm'),	label = 'pipe length (L)')
	surfaceRoughness = Quantity('Length', default = (25, 'um'),	label = 'surface roughness')
	pipeMaterial = ObjectReference(Solids, default = 'StainlessSteel304', label = 'pipe material')
	TWall = Quantity('Temperature', default = (50, 'degC'), label = 'pipe temeprature')	
	pipeInput = FieldGroup([internalDiameter, externalDiameter, length,	pipeMaterial,
		surfaceRoughness, TWall], label = "Pipe")
	#####
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
	inletPressure = Quantity('Pressure', default = (2, 'bar'), label = 'inlet pressure') 
	inletTemperature = Quantity('Temperature', default = (15, 'degC'), label = 'inlet temperature')					
	inletMassFlowRate = Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'inlet mass flow rate')
	ambientTemperature = Quantity('Temperature', default = (15, 'degC'), label = 'ambient temperature')
	flowInput = FieldGroup([fluidName, inletPressure, inletTemperature,	inletMassFlowRate], label = 'Flow')
	#####	
	inputs = SuperGroup([pipeInput, flowInput])
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	internalSurfaceArea = Quantity('Area', label = 'internal surface area')
	externalSurfaceArea = Quantity('Area', label = 'external surface area')
	crossSectionalArea = Quantity('Area', label = 'cross sectional area')
	pipeSolidMass = Quantity('Mass', label = 'pipe solid mass')
	pipeOutput = FieldGroup([internalSurfaceArea, externalSurfaceArea,
		crossSectionalArea, pipeSolidMass], label = "Pipe")
	#####
	inletDensity = Quantity('Density', label = 'inlet density')
	fluidVolume = Quantity('Volume', label = 'fluid volume', default = (1, 'L'))
	fluidMass = Quantity('Mass', label = 'fluid mass')
	massFlowRate = Quantity('MassFlowRate', label = 'mass flow rate', default = (1, 'kg/h'))
	volumetricFlowRate = Quantity('VolumetricFlowRate', label = 'volumetric flow rate', default = (1, 'L/h'))
	flowVelocity = Quantity('Velocity', label = 'flow velocity')
	Re = Quantity('Dimensionless', label = 'Reynolds number')
	zeta = Quantity('Dimensionless', label = 'friction factor')
	dragCoefficient = Quantity('Dimensionless', label = 'drag coefficient')
	pressureDrop = Quantity('Pressure', label = 'pressure drop')
	outletPressure = Quantity('Pressure', label = 'outlet pressure')
	outletTemperature  = Quantity('Temperature', label = 'outlet temperature', default = (1, 'degC'))
	flowOutput = FieldGroup([fluidVolume, inletDensity, fluidMass, massFlowRate, volumetricFlowRate, 
		flowVelocity, Re, zeta, dragCoefficient, pressureDrop, outletPressure], label = "Flow")
	#####
	inletEnthalpy = Quantity('SpecificEnthalpy', label = 'inlet enthalpy')
	outletEnthalpy = Quantity('SpecificEnthalpy', label = 'outlet enthalpy')
	outletTemperature = Quantity('Temperature', label = 'outlet temperature')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')	
	Nu = Quantity('Dimensionless', label = 'Nusselt number')
	alpha = Quantity('HeatTransferCoefficient', label = 'convection coefficient')
	QDot = Quantity('HeatFlowRate', label = 'heat flow rate')
	heatExchangeOutput = FieldGroup([Pr, Nu, alpha, QDot, outletTemperature], label = "Values")	
	#####
	flowResistanceResults = SuperGroup([pipeOutput, flowOutput], label="Flow resistance")
	heatExchangeResults = SuperGroup([heatExchangeOutput], label="Heat exchange")
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [flowResistanceResults, heatExchangeResults])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]

	############# Methods ###############
	def compute(self):
		self.computeGeometry()
		self.computePressureDrop()
		self.computeHeatExchange()
		
	def computeGeometry(self):
		if (self.externalDiameter <= self.internalDiameter):
			raise ValueError('External diameter value must be bigger than internal diameter value.')
		self.crossSectionalArea = np.pi / 4 * self.internalDiameter ** 2
		self.fluidVolume = self.crossSectionalArea * self.length
		self.internalSurfaceArea = np.pi * self.internalDiameter * self.length
		self.externalSurfaceArea = np.pi * self.externalDiameter * self.length
		self.pipeSolidMass = self.pipeMaterial['refValues']['density'] \
			* np.pi / 4 * (self.externalDiameter**2 - self.internalDiameter**2) * self.length
			
	def computePressureDrop(self):
		upstreamState = FluidState(self.fluidName)
		upstreamState.update_Tp(self.inletTemperature, self.inletPressure)

		self.inletDensity = upstreamState.rho
		self.massFlowRate = self.inletMassFlowRate
		self.fluidMass = self.fluidVolume * self.inletDensity
		self.volumetricFlowRate = self.massFlowRate / self.inletDensity	
		self.flowVelocity = self.massFlowRate / (self.inletDensity * self.crossSectionalArea )
		self.Re = self.inletDensity * self.flowVelocity * self.internalDiameter / upstreamState.mu
		self.zeta = PipeFlow.ChurchilCorrelation(self.Re, self.internalDiameter, self.surfaceRoughness)
		self.dragCoefficient = self.zeta * self.length / self.internalDiameter
		self.pressureDrop = self.dragCoefficient * self.inletDensity * self.flowVelocity * self.flowVelocity / 2
		self.outletPressure = self.inletPressure - self.pressureDrop
		return self.pressureDrop
	
	def computeHeatExchange(self):
		upstreamState = FluidState(self.fluidName)
		upstreamState.update_Tp(self.inletTemperature, self.inletPressure)
		
		self.inletEnthalpy = upstreamState.h
		self.Pr = upstreamState.Pr
		self.cond = upstreamState.cond
		
		# Determining Nusselt number
		if (self.Re <= 2.3e3):
			# laminar flow
			self.Nu = 3.66
		elif (self.Re > 2.3e3 and self.Re < 1e4):
			# transition	
			interpCoeff = (self.Re - 2.3e3) / (1e4 - 2.3e3) 
			Nu_low = 3.66
			eps = (1.8 * 4 - 1.5)**(-2)
			Nu_high = ((eps / 8.) * 1e4 * self.Pr) / (1 + 12.7 * math.sqrt(eps / 8.) * (self.Pr**(2 / 3.) - 1)) * \
			(1 + (self.internalDiameter / self.length)**(2 / 3.))
			self.Nu = interpCoeff * Nu_high + (1 - interpCoeff) * Nu_low
		elif (self.Re >= 1e4 and self.Re <= 1e6):
			# turbulent flow
			eps = (1.8 * math.log(self.Re, 10) - 1.5)**(-2)
			self.Nu = ((eps / 8.) * self.Re * self.Pr) / (1 + 12.7 * math.sqrt(eps / 8.) * (self.Pr**(2 / 3.) - 1)) * \
			(1 + (self.internalDiameter / self.length)**(2 / 3.))
		elif (self.Re > 1e6):
			raise ValueError("Outside range of validity")
		
		self.alpha = self.cond * self.Nu / self.internalDiameter
		self.QDot = self.alpha * self.internalSurfaceArea * (self.inletTemperature - self.TWall)
		
		self.outletEnthalpy = self.inletEnthalpy - (self.QDot / self.massFlowRate)
		
		downstreamState = FluidState(self.fluidName)
		downstreamState.update_ph(self.outletPressure, self.outletEnthalpy)
		self.outletTemperature = downstreamState.T
		
	@staticmethod
	def ChurchilCorrelation(Re, d, epsilon):
		theta1 = np.power(2.457 * np.log(np.power(7.0 / Re, 0.9) + 0.27 * epsilon / d), 16)
		theta2 = np.power(37530.0 / Re, 16)
		zeta = 8 * np.power(np.power((8.0 / Re), 12) + 1 / np.power((theta1 + theta2), 1.5) , 1./12)
		return zeta

	@staticmethod
	def testChurchilCorrelation():
		Re = np.logspace(2, 6, 1000, base = 10.0)
		d = 5e-3
		epsilon = 25e-7
		zeta = 0 * Re
		for i in range(len(Re)):
			zeta[i] = PipeFlow.ChurchilCorrelation(Re[i], d, epsilon)
		plt.loglog(Re, zeta)
		plt.show()
	
	@staticmethod
	def testComputePressureDrop():
		pipe = PipeFlow()
		pipe.computeGeometry()
		pipe.computePressureDrop()
		print pipe.outletPressure
	
	@staticmethod
	def testMetamodel():
		#a = PipeFlow(5e-3, 6e-3, 1.0, 2700)
		a = PipeFlow(internalDiameter = (3, 'in'))
		inputs = a.group2Json(PipeFlow.inputs)
		results = a.group2Json(PipeFlow.results)
		print json.dumps(inputs, indent = 4)
		print json.dumps(results, indent = 4)
		
class Orifice(object):
	def __init__(self, diameter, cq):
		self.diameter = diameter
		self.cq = cq
	
	def computeMassFlowRate(self):
		gamma = 1.33
		pUp = 300e5
		pDown = np.linspace(100e5, 299.9e5, 1000)
		ratio = pDown/pUp
		delta = 1 - ratio
		dp = pUp - pDown
		R_g = 1
		crit_ratio = np.power(2/(gamma + 1), gamma / (gamma - 1))
		crit_delta = 1 - crit_ratio
		crit_dp = pUp * crit_delta
		print ('crit. ratio = {0}'.format(crit_ratio))
		cm = np.sqrt(2 * gamma / (R_g * (gamma - 1))) * np.sqrt(np.power(ratio, 2 / gamma) - np.power(ratio, (gamma + 1) / gamma))
		cm_crit = np.sqrt(2 * gamma / (R_g * (gamma + 1))) * np.power(2 / (gamma + 1), 1 / (gamma - 1)) * (1 + 0 * cm)
		cm_approx = np.sqrt(1 - np.power(1 - delta/crit_delta, 2)) * cm_crit
		plt.plot(ratio, cm, 'r')
		plt.plot(ratio, cm_crit, 'm')
		plt.plot(ratio, cm_approx, 'g')
		plt.plot([crit_ratio, crit_ratio], [0, np.max(cm) * 1.1], 'b')
		plt.show()
	
	@staticmethod
	def test():
		orifice = Orifice(3e-3, 1.0)
		orifice.computeMassFlowRate()

class Elbow(object):
	#r_d_90 = np.array([1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20])
	#C_d_90 = np.array([20, 14, 12, 12, 14, 17, 24, 30, 34, 38, 42, 50])
	#interp90 = scipy.interpolate.interp1d(r_d_90, C_d_90)
	A1 = scipy.interpolate.interp1d(
			np.array([0, 20, 30, 45, 60, 75, 90, 110, 130, 150, 180]),
			np.array([0, 0.31, 0.45, 0.60, 0.78, 0.90, 1.0, 1.13, 1.20, 1.28, 1.40])
	)
	B1 = scipy.interpolate.interp1d(
			np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
			np.array([1.18, 0.77, 0.51, 0.37, 0.28, 0.21, 0.19, 0.17, 0.15, 0.11, 0.09, 0.07, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03])
	)
	@staticmethod
	def kDelta(relRoughness):
		if (relRoughness < 1e-3):
			result = 1 + 1e3 * relRoughness
		else:
			result = 2
		return result
	
	@staticmethod
	def kRe(Re):
		result = 1.3 - 0.29 * np.log(1e-5 * Re)
		if (result < 1.0):
			result = 1.0;
		return result

	def __init__(self, internalDiameter, bendRadius, bendAngleDeg, surfaceRoughness = 0.025):
		self.internalDiameter = internalDiameter
		self.bendRadius = bendRadius
		self.bendAngleDeg = bendAngleDeg
		self.surfaceRoughness = surfaceRoughness
		self.crossSectionalArea = np.pi / 4 * self.internalDiameter**2
		self.length = self.bendAngleDeg / 180.0 * np.pi * self.bendRadius
		
		self.a1 = Elbow.A1(self.bendAngleDeg)
		self.b1 = Elbow.B1(self.bendRadius / self.internalDiameter)
		self.kd = Elbow.kDelta(self.surfaceRoughness / self.internalDiameter)
		
		print ("R_0/d", self.bendRadius / self.internalDiameter)		
		
	def setUpstreamState(self, pressure, temperature):
		fluidState = MediumState(getFluid('parahydrogen'))
		fluidState.update_Tp(temperature, pressure)
		return fluidState

	def computePressureDrop(self, upstreamState, mDot):
		self.flowVelocity = mDot / (upstreamState.rho * self.crossSectionalArea )
		self.Re = upstreamState.rho * self.flowVelocity * self.internalDiameter / upstreamState.mu
		print ('Re=', self.Re)
		
		self.cFriction = PipeFlow.ChurchilCorrelation(self.Re, self.internalDiameter, self.surfaceRoughness) \
			* self.length / self.internalDiameter
		self.cLocal = self.a1 * self.b1 * self.kd * Elbow.kRe(self.Re)
		self.dragCoefficient =  self.cFriction + self.cLocal
		self.pressureDrop = self.dragCoefficient * upstreamState.rho * self.flowVelocity * self.flowVelocity / 2
	
		print ('cLocal=', self.cLocal)
		print ('cFriction=', self.cFriction)
		print ('dp[bar]=', self.pressureDrop/1e5)
	
	@staticmethod	
	def test():
		#a = Elbow(internalDiameter = 5.08e-2, bendRadius = 81.28e-2, bendAngleDeg = 30, surfaceRoughness = 0.00005)
		b = Elbow(internalDiameter = 3e-3, bendRadius = 16.0e-3, bendAngleDeg = 90, surfaceRoughness = 25e-6)
		upState = b.setUpstreamState(3e7, 288)
		b.computePressureDrop(upState, 100./3600)

class PipeFlowDoc(RestBlock):
	name = 'PipeFlowDoc'
	label = 'Pipe Flow (Docs)'
	template = 'documentation/html/PipeFlowDoc.html'
		
if __name__ == '__main__':
	#PipeFlow.testChurchilCorrelation()
	#Orifice.test()
	#Elbow.test()
	PipeFlow.testComputePressureDrop()
