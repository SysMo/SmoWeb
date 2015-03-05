'''
Created on Mar 5, 2015

@author: AtanasPavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from DynamicalModel import DynamicalModel
from smo.volume.Structures import FluidPort, FluidFlow

class FluidPistonPump(DynamicalModel):
	def __init__(self, fluid):
		self.fluid = fluid
		self.fStateOut = FluidState(fluid)
		self.flow = FluidFlow()
		self.portOut = FluidPort('R', self.flow)
		self.portIn = FluidPort('R', -self.flow)
	def compute(self):
		self.VDot = self.n * self.V
		self.mDot = self.VDot * self.portIn.state.rho
		self.fStateOut.update_ps(self.portOut.state.p, self.portIn.state.s)
		self.HDot = self.flow.mDot * self.fStateOut.h
		self.flow.mDot = self.mDot
		self.flow.HDot = self.HDot
