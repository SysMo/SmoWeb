'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMot Ltd., Bulgaria
'''
import smo.media.CoolProp as CP

class FluidFlow(object):
	def __init__(self, mDot = 0., HDot = 0.):
		self.mDot = float(mDot)
		self.HDot = float(HDot)
	
	def __add__(self, other):
		return FluidFlow(
				mDot = self.mDot + other.mDot,
				HDot = self.HDot + other.HDot
			)
	def __iadd__(self, other):
		self.mDot += other.mDot
		self.HDot += other.HDot
		return self
	
	def __neg__(self):
		return ReverseFluidFlow(self)
	
	def clear(self):
		self.mDot = 0.
		self.HDot = 0.

class ReverseFluidFlow(object):
	def __init__(self, flow):
		self.flow = flow
	@property
	def mDot(self):
		return -self.flow.mDot
	@property
	def HDot(self):
		return -self.flow.HDot

class HeatFlow(object):
	def __init__(self, qDot = 0.):
		self.QDot = float(qDot)
		
	def __add__(self, other):
		return HeatFlow(qDot = self.QDot + other.QDot)
	
	def __iadd__(self, other):
		self.QDot += other.QDot
		return self

	def __neg__(self):
		return ReverseHeatFlow(self)

	def clear(self):
		self.QDot = 0.

class ReverseHeatFlow(object):
	def __init__(self, flow):
		self.flow = flow
	@property
	def QDot(self):
		return -self.flow.QDot

class ThermalState(object):
	def __init__(self, T = 288.15):
		self.T = float(T)

class Port(object):
	def connect(self, otherPort):
		self.otherPort = otherPort
		otherPort.otherPort = self

class RCPort(Port):
	stateType = None
	flowType = None
	def __init__(self, portType, outVar = None):
		if (portType in 'C', 'R'):
			self.portType = portType
		else:
			raise ValueError("portType for {} port must be 'C' or 'R', {} given instead".format(self.portDomain, portType))
		
		if (portType == 'C'):
			if (outVar is None):
				raise ValueError("A 'C' type port must be given a state instance")
			else:
				self.state = outVar
				self.flow = None
		else: # (portType == 'R')
			if (outVar is None):
				outVar = self.flowType()
			self.state = None
			self.flow = outVar
		
	def connect(self, otherPort):
		if (isinstance(otherPort, DynamicCPort)):
			otherPort.connect(self)
			return
		if (self.domain == otherPort.domain):
			if (self.portType == 'C' and otherPort.portType == 'R'):
				self.flow = otherPort.flow
				otherPort.state = self.state
			elif (self.portType == 'R' and otherPort.portType == 'C'):
				self.state = otherPort.state
				otherPort.flow = self.flow
			else:
				raise ValueError("Incompatible port types: {} cannot be connected to {}".format(
						self.portType, otherPort.portType))
			super(RCPort, self).connect(otherPort)
		else:
			raise ValueError('Incompatible port domains: {} cannot be connected to {}'.format(
					self.domain, otherPort.domain))
			
class DynamicCPort(object):
	def __init__(self, portClass, state):
		self.state = state
		self.portClass = portClass
		self.totalFlow = portClass.flowType()
		self.ports = []
		self.portType = 'C'
	
	def connect(self, other):
		port = self.portClass('C', self.state)
		port.connect(other)
		self.ports.append(port)
	
	@property
	def flow(self):
		self.totalFlow.clear()
		for port in self.ports:
			self.totalFlow += port.flow
		return self.totalFlow
		
class ThermalPort(RCPort):
	domain = 'Thermal'
	stateType = ThermalState
	flowType = HeatFlow
		
class FluidPort(RCPort):
	domain = 'Fluid'
	stateType = CP.FluidState
	flowType = FluidFlow
	
