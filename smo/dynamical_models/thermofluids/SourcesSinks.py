'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd., Bulgaria
'''
import smo.dynamical_models.core.DynamicalModel as dm
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from Structures import FluidFlow, FluidPort
from Structures import ThermalPort,	ThermalState

class TemperatureSource(dm.DynamicalModel):
	def __init__(self, T):
		self.T = T
		self.port1 = ThermalPort('C', ThermalState())
	def computeState(self):
		self.port1.state.T = self.T

class FlowSource(dm.DynamicalModel):
	'''
	Flow source or sink
	'''
	def __init__(self, fluid, mDot = 0, TOut = None):
		self.fluid = fluid
		self.fState = FluidState(fluid)
		self.TOutModel = lambda obj: TOut
		self.mDot = mDot
		self.flow = FluidFlow(mDot = self.mDot)
		self.port1 = FluidPort('R', self.flow) 
		
	def compute(self):
		self.extState = self.port1.state
		if (self.mDot > 0):
			self.fState.update_Tp(self.TOutModel(self), self.extState.p)
			self.HDot = self.mDot * self.fState.h
		else:
			self.HDot = self.mDot * self.extState.h
		self.flow.mDot = self.mDot
		self.flow.HDot = self.HDot
		
class FluidStateSource(dm.DynamicalModel):
	TP = 1
	PQ = 2
	TQ = 3
	def __init__(self, fluid, sourceType):
		self.fluid = fluid
		self.fState = FluidState(fluid)
		self.port1 = FluidPort('C', self.fState)
		self.sourceType = sourceType 
	
	def computeState(self):
		if (self.sourceType == self.TP):
			self.fState.update_Tp(self.TIn, self.pIn)
		elif (self.sourceType == self.PQ):
			self.fState.update_pq(self.pIn, self.qIn)
		elif (self.sourceType == self.TQ):
			self.fState.update_Tq(self.TIn, self.qIn)
		
