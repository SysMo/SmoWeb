import numpy as np
from smo.model.model import NumericalModel
from smo.model.fields import *
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from smo.media.SimpleMaterials import Fluids

class GasConduction(NumericalModel):
	fluidName = Choices(Fluids, default = 'Helium', label = 'fluid')
	p = Quantity('Pressure', default = (1e5, 'Pa'), label = 'pressure')
	T1 = Quantity('Temperature', default = (273, 'K'), label = 'temperature 1')
	T2 = Quantity('Temperature', default = (278, 'K'), label = 'temperature 2')
	g1 = FieldGroup([fluidName, p, T1, T2], label = 'Gas')

	d = Quantity('Length', default = (0.01, 'm'), label = 'distance')	
	a1 = Quantity(default = 1, label = 'accomodation coeff 1')
	a2 = Quantity(default = 1, label = 'accomodation coeff 2')
	g2 = FieldGroup([d, a1, a2], label = 'Geometry')
	
	inputs = SuperGroup([g1, g2])
	###########
	T = Quantity('Temperature', default = (273, 'K'), label = 'mean temperature')
	rho = Quantity('Density', label = 'density')
	mu = Quantity('DynamicViscosity', label = 'viscosity')
	c = Quantity('Velocity', label = 'mean molecular velocity')
	l = Quantity('Length', label = 'mean free path')
	r1 = FieldGroup([rho, mu, c, l], label = 'Gas properties')

	Kn = Quantity(label = 'Knudsen number')
	f = Quantity(label = 'corr. factor (f)')
	fct = Quantity(label = 'q / q<sub>cont</sub>')
	qDot = Quantity('HeatFluxDensity', label = 'heat flux density')
	qDotFM = Quantity('HeatFluxDensity', label = 'heat flux density (FM)')
	r2 = FieldGroup([Kn, f, fct, qDot, qDotFM], label = 'Heat transfer')
	
	results = SuperGroup([r1, r2])
	
	def compute(self):
		R = 8.314462
		mMol = Fluid(self.fluidName).molarMass / 1e3
		self.T = (self.T1 + self.T2) / 2
		state = FluidState(self.fluidName)
		state.update_Tp(self.T, self.p)

		self.rho = state.rho
		self.mu = state.mu
		self.c = np.sqrt(8 * R * state.T / (np.pi * mMol))
		self.l = (2 * self.mu) / (state.rho * self.c)
		
		self.Kn = self.l / self.d
		self.f = 16./15 * (1 / state.Pr) * (state.gamma / (state.gamma + 1))
		self.fct = 1. / (1 + 15./4 * self.Kn) #* self.f
				
		self.qDot = self.fct * state.cond / self.d * np.abs(self.T1 - self.T2)
		
		Rg = R / mMol
		self.qDotFM = (state.cp - Rg / 2 ) * state.p / np.sqrt(2 * np.pi * Rg * self.T) * np.abs(self.T1 - self.T2) 
	
	@staticmethod
	def test():
		gc = GasConduction()
		gc.fluidName = 'Helium'
		gc.compute()
		print 
		print("rho = {0}".format(gc.rho))
		print("mu = {0}".format(gc.mu))
		print("c = {0}".format(gc.c))
		print("l = {0}".format(gc.l))
	

if __name__ == '__main__':
	GasConduction.test()
