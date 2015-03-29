'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd., Bulgaria
'''
import smo.media.CoolProp as CP
import smo.dynamical_models.core as DMC
from smo.dynamical_models.thermofluids import Structures as DMS
from smo.util import AttributeDict

class TemperatureSource(DMC.DynamicalModel):
	def __init__(self, T):
		self.T = T
		self.port1 = DMS.ThermalPort('C', DMS.ThermalState())
		
	def computeState(self):
		self.port1.state.T = self.T

class FlowSource(DMC.DynamicalModel):
	'''
	Flow source or sink
	'''
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.fluid = params.fluid
		self.fState = CP.FluidState(self.fluid)
		self.TOutModel = lambda obj: params.TOut
		self.mDot = params.mDot
		self.flow = DMS.FluidFlow(mDot = self.mDot)
		self.port1 = DMS.FluidPort('R', self.flow) 
		
	def compute(self):
		self.extState = self.port1.state
		if (self.mDot > 0):
			self.fState.update_Tp(self.TOutModel(self), self.extState.p)
			self.HDot = self.mDot * self.fState.h
		else:
			self.HDot = self.mDot * self.extState.h
		self.flow.mDot = self.mDot
		self.flow.HDot = self.HDot
		
class FluidStateSource(DMC.DynamicalModel):
	TP = 1
	PQ = 2
	TQ = 3
	
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.fluid = params.fluid
		self.fState = CP.FluidState(self.fluid)
		self.port1 = DMS.FluidPort('C', self.fState)
		self.sourceType = params.sourceType 
	
	def computeState(self):
		if (self.sourceType == self.TP):
			self.fState.update_Tp(self.TIn, self.pIn)
		elif (self.sourceType == self.PQ):
			self.fState.update_pq(self.pIn, self.qIn)
		elif (self.sourceType == self.TQ):
			self.fState.update_Tq(self.TIn, self.qIn)
		
