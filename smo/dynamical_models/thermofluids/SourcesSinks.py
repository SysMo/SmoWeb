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
	# Source types by state variables
	TP = 1
	PQ = 2
	TQ = 3
	
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.fluid = params.fluid
		self.fState = CP.FluidState(self.fluid)
		self.port1 = DMS.FluidPort('C', self.fState)
		
	def initState(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.setState(params)
		self.compute()
		
	def setState(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
		
		self.sourceType = params.sourceType 
		if (self.sourceType == self.TP):
			self.T = params.T
			self.p = params.p	
		elif (self.sourceType == self.PQ):
			self.p = params.p
			self.q = params.q
		elif (self.sourceType == self.TQ):
			self.T = params.T
			self.q = params.q
	
	def compute(self):
		if (self.sourceType == self.TP):
			self.fState.update_Tp(self.T, self.p)
		elif (self.sourceType == self.PQ):
			self.fState.update_pq(self.p, self.q)
		elif (self.sourceType == self.TQ):
			self.fState.update_Tq(self.T, self.q)
	
