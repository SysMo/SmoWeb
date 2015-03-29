'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.media.CoolProp as CP
import smo.dynamical_models.core as DMC
from smo.dynamical_models.thermofluids import Structures as DMS
from smo.util import AttributeDict

class FluidChamber(DMC.DynamicalModel):
	V = DMC.RealVariable(causality = DMC.Causality.parameter, variability = DMC.Variability.constant)
	T = DMC.RealVariable(causality = DMC.Causality.input, variability = DMC.Variability.continuous)
	rho = DMC.RealVariable(causality = DMC.Causality.input, variability = DMC.Variability.continuous)
	TDot = DMC.RealVariable(causality = DMC.Causality.output, variability = DMC.Variability.continuous)
	rhoDot = DMC.RealVariable(causality = DMC.Causality.output, variability = DMC.Variability.continuous)
	p = DMC.RealVariable(causality = DMC.Causality.output, variability = DMC.Variability.continuous)
	m = DMC.RealVariable(causality = DMC.Causality.output, variability = DMC.Variability.continuous)
	
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.V = params.V
		if (isinstance(params.fluid, CP.Fluid)):
			self.fluid = params.fluid
		else:
			self.fluid = CP.Fluid(params.fluid)
			
		self.fState = CP.FluidState(self.fluid)
		self.fluidPort = DMS.DynamicCPort(DMS.FluidPort, state = self.fState)
	
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
		
	def compute(self):
		QDot = 0
		self.computeDerivatives(self.fluidPort.flow.mDot, self.fluidPort.flow.HDot, QDot)

	def computeDerivatives(self, mDot = 0, HDot = 0, QDot = 0, VDot = 0):
		c1 = mDot / self.m - VDot / self.V;
		UDot = HDot + QDot - self.fState.p * VDot;
		self.rhoDot = self.fState.rho * c1;
		vDot = - self.rhoDot / (self.fState.rho * self.fState.rho);
		uDot = (UDot - mDot * self.fState.u) / self.m;
		k2 = (self.fState.T * self.fState.dpdT_v - self.fState.p) * vDot;
		self.TDot = (uDot - k2) / self.fState.cv;
			

def testFluidChamber_Fueling():
	from SourcesSinks import FlowSource

	print "=== START: Test FluidChamber ==="
	
	# Open csv file
	import csv
	csvfile = open('./test/FluidChamber_Results.csv', 'wb')
	csv_writer = csv.writer(csvfile, delimiter=',')
	csv_writer.writerow(["Time[s]", "Tank pressure [bar]", "Tank temperature [K]", "Tank density [kg/m**3]", "Inlet enthalpy flow rate [W]"])
	
	# Parameters
	mDot = 50./3600 #[kg/s]
	Tin = 250.0 #[K]

	# Create Fluid
	fluid = CP.Fluid('ParaHydrogen')
	# Create fluid source
	fluidSource = FlowSource(fluid, mDot = mDot, TOut = Tin)
	# Create tank
	tank = FluidChamber(
		fluid = fluid, 
		V = 0.100 #[m**3] 100 L
	)
	# Connect tank and flow source
	tank.fluidPort.connect(fluidSource.port1)
	
	# Initial tank state
	TTank_init = 300 #[K]
	pTank_init = 2e5 #[Pa]
	tank.initialize(TTank_init, pTank_init)
	rhoTank = tank.fState.rho
	TTank = tank.fState.T

	t = 0.0
	dt = 0.01
	tPrintInterval = dt * 100
	tNextPrint = 0
	
	# Run simulation
	while True:
		# Set tank state
		tank.setState(TTank, rhoTank)
		
		# Set source state
		fluidSource.compute()
		
		# Write to csv file
		if t >= tNextPrint:
			csv_writer.writerow([t, tank.p / 1.e5, tank.T, tank.rho, fluidSource.flow.HDot, fluidSource.fState.h])
			tNextPrint = t + tPrintInterval - dt/10
		t += dt
				
		# Compute tank
		tank.compute()
		if (tank.p > 200e5):
			break
		TTank += tank.TDot * dt
		rhoTank += tank.rhoDot *dt
		
	# Close csv
	csvfile.close()	
	print "=== END: Test FluidChamber ==="


if __name__ == '__main__':
	testFluidChamber_Fueling()