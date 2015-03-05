'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMot Ltd., Bulgaria
'''

from smo.media.CoolProp.CoolProp import FluidState
	
class FluidFlow(object):
	def __init__(self, mDot = 0, HDot = 0):
		self.mDot = mDot
		self.HDot = HDot
	
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
		self.mDot = 0
		self.HDot = 0

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
	def __init__(self, qDot = 0):
		self.qDot = qDot
		
	def __add__(self, other):
		return HeatFlow(qDot = self.qDot + other.qDot)
	
	def __iadd__(self, other):
		self.qDot += other.qDot
		return self

	def __neg__(self):
		return ReverseHeatFlow(self)

	def clear(self):
		self.qDot = 0

class ReverseHeatFlow(object):
	def __init__(self, flow):
		self.flow = flow
	@property
	def qDot(self):
		return -self.flow.qDot

class ThermalState(object):
	def __init__(self, T = 288.15):
		self.T = T

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
	stateType = FluidState
	flowType = FluidFlow
	
import unittest
class TestRCPort(unittest.TestCase):
	def setUp(self):
		fState = FluidState('Oxygen')
		tState = ThermalState()
		self.fp1 = FluidPort('C', fState)
		self.fp2 = FluidPort('R')
		self.fp3 = DynamicCPort(FluidPort, FluidState('Oxygen'))
		self.fp4 = FluidPort('R')
		self.tp1 = ThermalPort('C', tState)
		self.tp2 = ThermalPort('R')
		self.tp3 = ThermalPort('R')

		self.fp1.state.update_Tp(300, 2e5)
		self.fp2.flow.mDot = 3.0
		self.fp2.flow.HDot = 4.0e3
		self.fp4.flow.mDot = 5.0
		self.fp4.flow.HDot = 7.0e3
		self.tp1.state.T = 23

	def test1(self):
		self.fp1.connect(self.fp2)
		self.assertAlmostEqual(self.fp1.flow.mDot, self.fp2.flow.mDot)
		self.assertAlmostEqual(self.fp1.flow.HDot, self.fp2.flow.HDot)
		self.assertAlmostEqual(self.fp1.state.T, self.fp2.state.T)
		self.tp1.connect(self.tp2)
		self.assertAlmostEqual(self.tp1.flow.qDot, self.tp2.flow.qDot)
		self.assertAlmostEqual(self.tp1.state.T, self.tp2.state.T)
		
	def test2(self):
		with self.assertRaises(ValueError):
			self.fp1.connect(self.tp2)
		
	def test3(self):
		with self.assertRaises(ValueError):
			self.tp2.connect(self.tp3)
			
	def test4(self):
		self.fp2.connect(self.fp3)
		self.fp3.connect(self.fp4)
		self.assertAlmostEqual(self.fp3.flow.mDot, self.fp2.flow.mDot + self.fp4.flow.mDot)
		self.assertAlmostEqual(self.fp3.flow.HDot, self.fp2.flow.HDot + self.fp4.flow.HDot)
		