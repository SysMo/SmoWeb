from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState
import numpy as np

class GasConduction():
	def compute(self):
		R = 8.314462
		mMol = Fluid(self.fluidName).molarMass() / 1e3
		state = FluidState(self.fluidName)
		state.update_Tp(273, 1e5)
		self.rho = state.rho()
		self.mu = state.mu()
		self.c = np.sqrt(8 * R * state.T() / (np.pi * mMol))
		self.l = (2 * self.mu) / (state.rho() * self.c) 
	
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
