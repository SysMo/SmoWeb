'''
Created on Jun 4, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.dynamical_models.core.DynamicalModel import DynamicalModel
from smo.dynamical_models.core.Fields import Variability as VR, Causality as CS
import smo.dynamical_models.core.Fields as F 

class PressureSource(DynamicalModel):
	p = F.RealVariable(causality = CS.Output, variability = VR.Constant, default = 1e5)
	mDot = 	F.RealVariable(causality = CS.Input)
	port = F.Port([p, mDot])
	
class FlowSource(DynamicalModel):
	mDot = 	F.RealVariable(causality = CS.Output, variability = VR.Constant, default = 1.0)
	p = F.RealVariable(causality = CS.Input)
	port = F.Port([p, mDot])

class Valve(DynamicalModel):
	Kv = F.RealVariable(causality = CS.Parameter, variability = VR.Constant)
	VDot = F.RealVariable(causality = CS.Output)
	mDot1 = F.RealVariable(causality = CS.Output)
	mDot2 = F.RealVariable(causality = CS.Output)
	p1 = F.RealVariable(causality = CS.Input)
	p2 = F.RealVariable(causality = CS.Input)
	controlSignal = F.IntegerVariable(causality = CS.Input)
	port1 = F.Port([p1, mDot1])
	port2 = F.Port([p2, mDot2])
	controlPort = F.Port([controlSignal])

class WaterTower(DynamicalModel):
	ACrossSection = F.RealVariable(causality = CS.Parameter, variability = VR.Constant)
	hWater = F.RealState(start = 0.5)
	mDotIn = F.RealVariable(causality = CS.Input)
	mDotOut = F.RealVariable(causality = CS.Input)
	p = F.RealVariable(causality = CS.Output)
	portIn = F.Port([p, mDotIn])
	portOut = F.Port([p, mDotOut])
	
class FlowController(DynamicalModel):
	waterLevel = F.RealVariable(causality = CS.Input)
	valveOpen = F.IntegerVariable(causality = CS.Output)

class FluidSystem(DynamicalModel):
	source = F.SubModel(FlowSource)
	waterTower = F.SubModel(WaterTower)
	valveOut = F.SubModel(Valve)
	flowController = F.SubModel(FlowController)
	sink = F.SubModel(PressureSource)
	
	def __init__(self):
		self.source.port.connect(self.waterTower.portIn)
		self.waterTower.portOut.connect(self.valveOut.port1)
		self.valveOut.port2.connect(self.sink.port)
		self.waterTower.meta.hWater.connect(self.flowController.meta.waterLevel)
		self.flowController.meta.valveOpen.connect(self.valveOut.meta.controlPort)
		