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
	
	def initialize(self, T, p):
		self.T = T
		self.p = p
		self.fState.update_Tp(T, p)
		self.rho = self.fState.rho
		self.m = self.fState.rho * self.V
		
	def setState(self, T, rho):
		self.T = T
		self.rho = rho
		self.fState.update_Trho(T, rho)
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
			

def testFluidChamber():
	print "=== START: Test FluidChamber ==="
	
	# Open csv file
	import csv
	csvfile = open('./test/FluidChamber_Results.csv', 'wb')
	csv_writer = csv.writer(csvfile, delimiter=',')
	csv_writer.writerow(["Time[s]", "Tank pressure [bar]", "Tank temperature [K]", "Tank density [kg/m**3]", "Inlet enthalpy flow rate [W]"])
	
	# Create FluidStates
	fluid = Fluid('ParaHydrogen')
	fStateIn = FluidState(fluid)
	tank = FluidChamber(fluid)
	
	# Parameters
	mDot = 75/3600. #[kg/s]
	t = 0.0
	dt = 0.01
	tPrintInterval = dt*100
	tNextPrint = 0
	
	tank.V = 0.1155 #[m**3] 115.5 L
	TTank_init = 300 #[K]
	pTank_init = 20e5 #[Pa]
	Tin = 63.0 #[K]
	
	# Initial tank state
	tank.fState.update_Tp(TTank_init, pTank_init)
	rhoTank = tank.fState.rho
	TTank = tank.fState.T
	
	# Run simulation
	while True:
		# Set tank state
		tank.setState(TTank, rhoTank)
		
		# Set inlet state
		fStateIn.update_Tp(Tin, tank.p)
		HDotIn = mDot * fStateIn.h
		
		# Write to csv file
		if t >= tNextPrint:
			csv_writer.writerow([t, tank.p / 1.e5, tank.T, tank.rho, HDotIn])
			tNextPrint = t + tPrintInterval - dt/10
		t += dt
				
		# Compute tank
		tank.compute(mDot = mDot, HDot = HDotIn)
		if (tank.p > 300e5):
			break
		TTank += tank.TDot * dt
		rhoTank += tank.rhoDot *dt
		
	# Close csv
	csvfile.close()	
	print "=== END: Test FluidChamber ==="


if __name__ == '__main__':
	testFluidChamber()