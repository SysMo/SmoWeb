'''
Created on Jun 4, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.dynamical_models.core.DynamicalModel import DynamicalModel
from smo.dynamical_models.core.Fields import Variability as VR, Causality as CS
import smo.dynamical_models.core.Fields as F
import math as m

class PressureSource(DynamicalModel):
	p = F.RealVariable(causality = CS.Output, variability = VR.Constant, default = 1e5)
	mDot = 	F.RealVariable(causality = CS.Input)
	port = F.Port([p, mDot])
	
class FlowSource(DynamicalModel):
	mDot = 	F.RealVariable(causality = CS.Output, variability = VR.Constant, default = 100.0)
	p = F.RealVariable(causality = CS.Input)
	port = F.Port([p, mDot])

class Valve(DynamicalModel):
	Kv = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 2000.)
	VDot = F.RealVariable(causality = CS.Output)
	mDot1 = F.RealVariable(causality = CS.Output)
	mDot2 = F.RealVariable(causality = CS.Output)
	p1 = F.RealVariable(causality = CS.Input)
	p2 = F.RealVariable(causality = CS.Input)
	controlSignal = F.RealVariable(causality = CS.Input, default = 1)
	port1 = F.Port([p1, mDot1])
	port2 = F.Port([p2, mDot2])

	def compute(self, t):
		N1 = 8.784e-07;
		if (self.p1 > self.p2):
			self.VDot = N1 * self.Kv * m.sqrt((self.p1 - self.p2) / 1.0)
			self.mDot2 = 1000 * self.VDot * self.controlSignal
			self.mDot1 = - self.mDot2
		else:
			self.VDot = 0
			self.mDot2 = 0
			self.mDot1 = 0
		print self.mDot1

class WaterTower(DynamicalModel):
	ACrossSection = F.RealVariable(causality = CS.Parameter, variability = VR.Constant,
					 default = 1.0)
	hWater = F.RealState(start = 0.5)
	mDotIn = F.RealVariable(causality = CS.Input)
	mDotOut = F.RealVariable(causality = CS.Input)
	p = F.RealVariable(causality = CS.Output)
	portIn = F.Port([p, mDotIn])
	portOut = F.Port([p, mDotOut])
	
	@F.Function(inputs = [hWater], outputs = [p])
	def compute_p(self, t):
		self.p = 1e5 + 1000 * 9.8 * self.hWater

	def compute(self, t):
		self.der.hWater = (self.mDotIn + self.mDotOut) / 1000. / self.ACrossSection
		
class FlowController(DynamicalModel):
	waterLevel = F.RealVariable(causality = CS.Input)
	valveOpen = F.RealVariable(causality = CS.Output, default = 1)
	
	
	def detectLevelEvent(self):
		if (self.valveOpen > 0.5):
			return self.waterLevel - 0.35
		else:
			return self.waterLevel - 0.5
	
	@F.StateEvent(locate = detectLevelEvent)
	def onLevelEvent(self):
		self.valveOpen = 1 - self.valveOpen

class FluidSystem(DynamicalModel):
	source = F.SubModel(FlowSource)
	waterTower = F.SubModel(WaterTower)
	valveOut = F.SubModel(Valve)
	flowController = F.SubModel(FlowController)
	sink = F.SubModel(PressureSource)
	
	def __init__(self):
		self.source.meta.port.connect(self.waterTower.meta.portIn)
		self.waterTower.meta.portOut.connect(self.valveOut.meta.port1)
		self.valveOut.meta.port2.connect(self.sink.meta.port)
		self.waterTower.meta.hWater.connect(self.flowController.meta.waterLevel)
		self.flowController.meta.valveOpen.connect(self.valveOut.meta.controlSignal)
		