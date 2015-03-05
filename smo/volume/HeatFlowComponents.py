'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd., Bulgaria
'''

from Structures import FluidPort, ThermalPort

class ConvectionHeatTransfer(object):
	def __init__(self, **kwargs):
		
		self.hConv = kwargs.get('hConv', 100)
		self.A = kwargs.get('A', 1.0)

		self.fluidPort = FluidPort('R')
		self.wallPort = ThermalPort('R')
		
	def compute(self):
		# Read port variables
		self.TFluid = self.fluidPort.state.T
		self.TWall = self.wallPort.state.T
		# Compute heat flow
		self.QDot = self.hConv * self.A * (self.TWall - self.TFluid)
		# Write port variables
		self.fluidPort.flow.HDot = self.QDot
		self.fluidPort.flow.mDot = 0
		self.wallPort.flow.qDot = - self.QDot
	
	@staticmethod
	def test():
		from smo.media.CoolProp.CoolProp import FluidState
		c = ConvectionHeatTransfer()
		c.fluidPort.state = FluidState('ParaHydrogen')
		c.fluidPort.state.update_Tp(288, 1e5)
		c.wallPort.state.T = 350.0
		c.compute()
		print("qDotFluid = {}, qDotWall = {}".format(c.fluidPort.flow.HDot, c.wallPort.flow.qDot))

if __name__ == '__main__':
	ConvectionHeatTransfer.test()