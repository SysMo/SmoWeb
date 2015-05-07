'''
Created on May 3, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.dynamical_models.core as DMC
from smo.dynamical_models.core import Causality as C
from smo.dynamical_models.core import Variability as V
import networkx as nx

#from smo.dynamical_models.thermofluids import Structures as DMS

class ThermalMass(DMC.DynamicalModel):
	m = DMC.RealVariable(causality = C.Parameter, variability = V.Constant)
	T = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	QDot = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	TDot = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class ThermalConduction(DMC.DynamicalModel):
	k = DMC.RealVariable(causality = C.Parameter, variability = V.Constant)
	T1 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	T2 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	QDot = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class Integrator(DMC.DynamicalModel):
	xDot = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	x = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class ExampleCircuit(DMC.DynamicalModel):
	m1 = DMC.SubModel(ThermalMass)
	m2 = DMC.SubModel(ThermalMass)
	c = DMC.SubModel(ThermalConduction)
	integrator = DMC.SubModel(Integrator)

	def __init__(self):
		self.createModelGraph()
		self.plotModelGraph()
# 		self.connect(self.m1.T, self.c.T1)
# 		self.connect(self.c.QDot, self.m1.QDot)
# 		self.connect(self.c.QDot, self.m2.QDot)
# 		self.connect(self.m2.T, self.c.T2)
	
		
if __name__ == '__main__':
	cir = ExampleCircuit()
	#cir = ThermalMass()