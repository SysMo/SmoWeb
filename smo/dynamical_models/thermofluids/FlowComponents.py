'''
Created on Mar 5, 2015

@author: AtanasPavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.media.CoolProp as CP
import smo.dynamical_models.core as DMC
from smo.dynamical_models.thermofluids import Structures as DMS

class FluidPistonPump(DMC.DynamicalModel):
	def __init__(self, fluid, etaS, fQ):
		self.fluid = fluid
		self.etaS = etaS
		self.fQ = fQ
		self.fStateOut = CP.FluidState(fluid)
		self.flow = DMS.FluidFlow()
		self.portOut = DMS.FluidPort('R', self.flow)
		self.portIn = DMS.FluidPort('R', -self.flow)
	def compute(self):
		self.VDot = self.n * self.V
		self.mDot = self.VDot * self.portIn.state.rho
		self.fStateOut.update_ps(self.portOut.state.p, self.portIn.state.s)
		wIdeal = self.fStateOut.h - self.portIn.state.h
		wReal = wIdeal / self.etaS
		delta_hOut = wReal * (1 - self.fQ)
		self.fStateOut.update_ph(self.portOut.state.p, self.portIn.state.h + delta_hOut)
		self.TOut = self.fStateOut.T
		self.HDot = self.mDot * self.fStateOut.h
		self.flow.mDot = self.mDot
		self.flow.HDot = self.HDot

class FluidHeater(DMC.DynamicalModel):
	def __init__(self, fluid, condModel = None):
		self.fluid = fluid
		self.fStateIn = CP.FluidState(fluid)
		self.fStateOut = CP.FluidState(fluid)
		self.fStateDown = CP.FluidState(fluid)
		self.flowOut = DMS.FluidFlow()
		self.heatOut = DMS.HeatFlow()
		self.portIn = DMS.FluidPort('C', self.fStateDown)
		self.portOut = DMS.FluidPort('R', self.flowOut)
		self.thermalPort = DMS.ThermalPort('R', self.heatOut)
		if (condModel == None):
			self.condModel = lambda TFluid, TExt: 100.0
		else:
			self.condModel = condModel
		self.TOut = 0
		self.TIn = 0
			

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
			# Correction of the outlet temperature is too low or too high
			if ((self.QDot < 0 and self.TOut > TExt) or (self.QDot > 0 and self.TOut < TExt)):
				self.TOut = TExt
				self.fStateOut.update_Tp(self.TOut, self.portOut.state.p)
				self.HDotOut = self.mDot * self.fStateOut.h
				self.QDot = self.portIn.flow.HDot - self.HDotOut
		else:
			self.QDot = 0
			self.HDotOut = 0
			
		self.flowOut.mDot = self.mDot
		self.flowOut.HDot = self.HDotOut 
		self.heatOut.QDot = self.QDot