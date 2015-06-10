'''
Created on May 26, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.dynamical_models.core.DynamicalModel import DynamicalModel
from smo.dynamical_models.core.Fields import Variability as VR, Causality as CS
import smo.dynamical_models.core.Fields as F 
from smo.web.exceptions import ConnectionError
import math

class ForceSource(DynamicalModel):
	f = F.RealVariable(causality = CS.Output, variability = VR.Constant, default = -10.)
	x = F.RealVariable(causality = CS.Input)
	v = F.RealVariable(causality = CS.Input)
	p = F.Port([f, v, x])
	
class BoundMass(DynamicalModel):
	m = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 10.)
	f = F.RealVariable(causality = CS.Input, default = 10.)
	x = F.RealState(start = 0.1)
	v = F.RealState(start = 1.)
	p = F.Port([f, v, x])
	
	def compute(self, t):
		self.der.x = self.v
		self.der.v = self.f / self.m
	
	def checkBounce(self):
		return self.x
	
	@F.StateEvent(locate = checkBounce)
	def onBounce(self):
		if (self.v < 0):
			self.v = - 0.9 * self.v
	
class MechSystem(DynamicalModel):
	fs = F.SubModel(ForceSource)
	mass = F.SubModel(BoundMass)
	
	def __init__(self):
		self.fs.meta.p.connect(self.mass.meta.p)