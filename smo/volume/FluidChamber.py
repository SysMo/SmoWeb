'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

import DynamicalModel as dm
from smo.media.CoolProp.CoolProp import Fluid, FluidState

class FluidChamber(dm.DynamicalModel):
	V = dm.RealVariable(causality = dm.Causality.parameter, variability = dm.Variability.constant)
	T = dm.RealVariable(causality = dm.Causality.input, variability = dm.Variability.continuous)
	rho = dm.RealVariable(causality = dm.Causality.input, variability = dm.Variability.continuous)
	TDot = dm.RealVariable(causality = dm.Causality.output, variability = dm.Variability.continuous)
	rhoDot = dm.RealVariable(causality = dm.Causality.output, variability = dm.Variability.continuous)
	p = dm.RealVariable(causality = dm.Causality.output, variability = dm.Variability.continuous)
	m = dm.RealVariable(causality = dm.Causality.output, variability = dm.Variability.continuous)
	
	def __init__(self, fluid):
		if (isinstance(fluid, Fluid)):
			self.fluid = fluid
		else:
			self.fluid = Fluid(fluid)
		self.fState = FluidState(self.fluid)
	
	def setState(self, T, rho):
		self.fState.update_Trho(T, rho)
		self.T = T
		self.rho = rho
		self.p = self.fState.p
		self.m = self.fState.rho * self.V
		
	def compute(self, mDot = 0, HDot = 0, QDot = 0, VDot = 0):
		c1 = mDot / self.m - VDot / self.V;
		UDot = HDot + QDot - self.fState.p * VDot;
		self.rhoDot = self.fState.rho * c1;
		vDot = - self.rhoDot / (self.fState.rho * self.fState.rho);
		uDot = (UDot - mDot * self.fState.u) / self.m;
		k2 = (self.fState.T * self.fState.dpdT_v - self.fState.p) * vDot;
		self.TDot = (uDot - k2) / self.fState.cv;
			
def main():
	fluid = Fluid('ParaHydrogen')
	fIn = FluidState(fluid)
	ch = FluidChamber(fluid)
	ch.V = 0.1155

	mDot = 75./3600
	t = 0.0
	dt = 0.01
	
	TTank = 300.0
	pTank = 20e5
	Tin = 63.0
	# Initial tank state
	ch.fState.update_Tp(TTank, pTank)
	rhoTank = ch.fState.rho
	
	while True:
		# Set tank state
		ch.setState(TTank, rhoTank)
		# Set inlet state
		fIn.update_Tp(Tin, ch.p)
		HDotIn = mDot * fIn.h
		# Compute tank
		ch.compute(mDot = mDot, HDot = HDotIn)
		if (ch.fState.p > 300e5):
			break
		TTank += ch.TDot * dt
		rhoTank += ch.rhoDot *dt
	print (ch.fState.p, ch.fState.T)

if __name__ == '__main__':
	main()