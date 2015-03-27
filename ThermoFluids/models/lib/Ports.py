'''
Created on Mar 27, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

class FluidFlow(object):
	def __init__(self):
		self.mDot = 0
		#self.HDot = 0

class PortBase(object):
	pass

class ThermodynamicPort(PortBase):
	def __init__(self):
		self.state = None
		self.flow = None
