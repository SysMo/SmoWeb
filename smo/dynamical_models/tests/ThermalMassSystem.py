'''
Created on May 3, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.dynamical_models.core.DynamicalModel import DynamicalModel
from smo.dynamical_models.core.Fields import Variability as VR, Causality as CS
import smo.dynamical_models.core.Fields as F 
from smo.web.exceptions import ConnectionError
import math


class ThermalPort(F.Port):
	def __init__(self, subType, TVar, QVar):
		super(ThermalPort, self).__init__([TVar, QVar], subType)
	def checkConnect(self, other):
		if (isinstance(other, ThermalPort)):
			if (self.subType == 'R' and other.subType == 'C'):
				return True
			elif (self.subType == 'C' and other.subType == 'R'):
				return True
			else:
				raise ConnectionError('Only complementary ports can be connected')
		else:
			raise ConnectionError('Incompatible port types')

class HeatSource(DynamicalModel):
	T = F.RealVariable(causality = CS.Input)
	QDot = F.RealVariable(causality = CS.Output)
	p = ThermalPort('R', TVar = T, QVar = QDot)
	isHeating = F.IntegerVariable(default = 1)

	def compute(self, t):
		#self.QDot = 100 * math.sin(t / 1000)
		#self.QDot = 10 * (350 - self.T)
		self.QDot = 100 * (self.isHeating - 0.5)
	
	def checkState(self):
		newState = -1
		if (self.isHeating == 1 and self.T > 350):
			newState = 1
		elif (self.isHeating == 0 and self.T < 250):
			newState = 2
		return newState

	@F.StateEvent(locate = checkState)
	def onHeatSwitch(self):
		self.isHeating = self.checkState() - 1
		print ("isHeating = {}".format(self.isHeating))
			
		

class ThermalMass(DynamicalModel):
	m = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 10.)
	cp = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 100.)
	T = F.RealState(start = 300)
	QDot1 = F.RealVariable(causality = CS.Input)
	QDot2 = F.RealVariable(causality = CS.Input)
	p1 = ThermalPort('C', TVar = T, QVar = QDot1)
	p2 = ThermalPort('C', TVar = T, QVar = QDot2)
	
	def compute(self, t):
		self.der.T = (self.QDot1 + self.QDot2) / self.m / self.cp

class ThermalConduction(DynamicalModel):
	k = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 1)
	T1 = F.RealVariable(causality = CS.Input)
	QDot1 = F.RealVariable(causality = CS.Output)
	T2 = F.RealVariable(causality = CS.Input)
	QDot2 = F.RealVariable(causality = CS.Output)
	p1 = ThermalPort('R', TVar = T1, QVar = QDot1)
	p2 = ThermalPort('R', TVar = T2, QVar = QDot2)

	def compute(self, t):
		self.QDot1 = self.k * (self.T2 - self.T1)
		self.QDot2 = - self.QDot1
		
class Convection(DynamicalModel):
	hConv = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 10)
	area = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 0.2)
	pFluid = F.RealVariable(causality = CS.Input)
	TFluid = F.RealVariable(causality = CS.Input)
	TWall = F.RealVariable(causality = CS.Input)
	QFluid = F.RealVariable(causality = CS.Output)
	QWall = F.RealVariable(causality = CS.Output)
	portFluid = F.Port([pFluid, TFluid, QFluid])
	portWall = ThermalPort('R', TVar = TWall, QVar = QWall)
	
	def compute(self, t):
		self.QFluid = self.hConv * self.area * (self.TWall - self.TFluid)
		self.QWall = -self.QFluid

class FluidChamber(DynamicalModel):
	VFluid = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 0.1)
	pInit = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 300e5)
	molarMass = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 16e-3)
	RGas = F.RealVariable(causality = CS.Parameter, variability = VR.Constant)
	T = F.RealState(start = 300)
	rho = F.RealState(start = 1)
	p = F.RealVariable(causality = CS.Output)
	m = F.RealVariable(causality = CS.Output)
	QDotWall = F.RealVariable(causality = CS.Input)
	portWall = F.Port([p, T, QDotWall])

	def initialize(self):
		self.RGas = 8.13 / self.molarMass
		self.rho = self.pInit / (self.RGas * self.rho * self.T)

	@F.Function(inputs = [T, rho], outputs = [p])
	def setState(self, t):
		self.p = self.RGas * self.rho * self.T

	def compute(self, t):
		self.m = self.VFluid * self.rho
		self.der.rho = 0
		self.der.T = self.QDotWall / self.m / (5./2 * self.RGas)


class Tank(DynamicalModel):
	qSource = F.SubModel(HeatSource)
	m1 = F.SubModel(ThermalMass)
	m2 = F.SubModel(ThermalMass)
	c = F.SubModel(ThermalConduction)
	conv = F.SubModel(Convection)
	ch = F.SubModel(FluidChamber)

	def __init__(self):
		self.m1.meta.p1.connect(self.qSource.meta.p)
		self.m1.meta.p2.connect(self.c.meta.p1)
		self.c.meta.p2.connect(self.m2.meta.p1)
		self.m2.meta.p2.connect(self.conv.meta.portWall)
		self.ch.meta.portWall.connect(self.conv.meta.portFluid)


