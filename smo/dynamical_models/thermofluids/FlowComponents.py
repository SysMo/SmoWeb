'''
Created on Mar 5, 2015

@author: AtanasPavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.dynamical_models.DynamicalModel as dm
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from Structures import *

class FluidPistonPump(dm.DynamicalModel):
	def __init__(self, fluid):
		self.fluid = fluid
		self.fStateOut = FluidState(fluid)
		self.flow = FluidFlow()
		self.portOut = FluidPort('R', self.flow)
		self.portIn = FluidPort('R', -self.flow)
	def compute(self):
		self.VDot = self.n * self.V
		self.mDot = self.VDot * self.portIn.state.rho
		self.fStateOut.update_ps(self.portOut.state.p, self.portIn.state.s)
		self.TOut = self.fStateOut.T
		self.HDot = self.mDot * self.fStateOut.h
		self.flow.mDot = self.mDot
		self.flow.HDot = self.HDot

class FluidHeater(dm.DynamicalModel):
	def __init__(self, fluid, condModel = None):
		self.fluid = fluid
		self.fStateIn = FluidState(fluid)
		self.fStateOut = FluidState(fluid)
		self.fStateDown = FluidState(fluid)
		self.flowOut = FluidFlow()
		self.heatOut = HeatFlow()
		self.portIn = FluidPort('C', self.fStateDown)
		self.portOut = FluidPort('R', self.flowOut)
		self.thermalPort = ThermalPort('R', self.heatOut)
		if (condModel == None):
			self.condModel = lambda TFluid, TExt: 100.0
		else:
			self.condModel = condModel
			

	def setState(self):
		self.fStateDown.update_Trho(self.portOut.state.T, self.portOut.state.rho)
	
	def compute(self):
		self.mDot = self.portIn.flow.mDot
		if (self.mDot > 1e-12):
			hIn = self.portIn.flow.HDot / self.mDot
			self.fStateIn.update_ph(self.portOut.state.p, hIn)
			self.Tin = self.fStateIn.T
			TExt = self.thermalPort.state.T
			cond = self.condModel(self.Tin, TExt)
			self.QDot = cond * (self.Tin - TExt)
			self.HDotOut = self.portIn.flow.HDot - self.QDot
			hOut = self.HDotOut / self.mDot
			self.fStateOut.update_ph(self.portOut.state.p, hOut)
			self.TOut = self.fStateOut.T
		else:
			self.QDot = 0
			self.HDotOut = 0
			
		self.flowOut.mDot = self.mDot
		self.flowOut.HDot = self.HDotOut 
		self.heatOut.QDot = self.QDot