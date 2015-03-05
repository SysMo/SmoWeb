'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd., Bulgaria
'''
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from Structures import FluidFlow

class FlowSource(object):
	'''
	Flow source or sink
	'''
	def __init__(self, fluid, mDot = 0, TOut = None):
		self.fluid = fluid
		self.fState = FluidState(fluid)
		self.TOutModel = lambda obj: TOut
		self.connState = None
		self.flow = FluidFlow(mDot = mDot)
		
	def compute(self):
		if (self.flow.mDot > 0):
			print self.TOutModel(self)
			print self.connState.p
			self.fState.update_Tp(self.TOutModel(self), self.connState.p)
			self.flow.HDot = self.flow.mDot * self.fState.h
		else:
			self.flow.HDot = self.flow.mDot * self.connState.h
			
class FluidPistonPump(FlowSource):
	def compute(self):
		self.flow.mDot = self.n * self.V
		super(FluidPistonPump, self).compute()