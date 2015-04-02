'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd., Bulgaria
'''
import smo.media.CoolProp as CP
import smo.dynamical_models.core as DMC
from smo.dynamical_models.thermofluids import Structures as DMS
from smo.util import AttributeDict

class TwoPortHeatTransfer(DMC.DynamicalModel):
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.condModel = params.condModel	
		self.port1 = DMS.ThermalPort('R')
		self.port2 = DMS.ThermalPort('R')
		
	def compute (self):
		self.QDot = self.condModel(self.port1.state.T, self.port2.state.T)
		self.port1.flow.QDot = -self.QDot
		self.port2.flow.QDot = self.QDot
		
class ConvectionHeatTransfer(DMC.DynamicalModel):
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.hConv = params.hConv #convectin coefficient
		self.A = params.A #convection area

		self.fluidPort = DMS.FluidPort('R')
		self.wallPort = DMS.ThermalPort('R')
		
	def compute(self):
		# Read port variables
		self.TFluid = self.fluidPort.state.T
		self.TWall = self.wallPort.state.T
		# Compute heat flow
		self.QDot = self.hConv * self.A * (self.TWall - self.TFluid)
		# Write port variables
		self.fluidPort.flow.HDot = self.QDot
		self.fluidPort.flow.mDot = 0
		self.wallPort.flow.QDot = - self.QDot
	
	@staticmethod
	def test():
		c = ConvectionHeatTransfer()
		c.fluidPort.state = CP.FluidState('ParaHydrogen')
		c.fluidPort.state.update_Tp(288, 1e5)
		c.wallPort.state.T = 350.0
		c.compute()
		print("qDotFluid = {}, qDotWall = {}".format(c.fluidPort.flow.HDot, c.wallPort.flow.QDot))

if __name__ == '__main__':
	ConvectionHeatTransfer.test()