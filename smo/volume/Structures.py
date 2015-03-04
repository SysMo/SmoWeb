'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMot Ltd., Bulgaria
'''

class FluidFlow(object):
	def __init__(self, mDot = 0, HDot = 0):
		self.mDot = mDot
		self.HDot = HDot
		
class HeatFlow(object):
	def __init__(self, qDot = 0):
		self.qDot = qDot

class ThermalState(object):
	def __init__(self, T = 288.15):
		self.T = T
		
class ThermalPort(object):
	def __init__(self, state = None, flow = None):
		if (state is None):
			state = ThermalState()
		if (flow is None):
			flow = HeatFlow()
		self.state = state
		self.flow = flow