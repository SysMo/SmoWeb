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
	T = DMC.RealState(der = 'TDot')
	QDot = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	TDot = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class ThermalConduction(DMC.DynamicalModel):
	k = DMC.RealVariable(causality = C.Parameter, variability = V.Constant)
	T1 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	T2 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	QDot = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class ExampleCircuit(DMC.DynamicalModel):
	m1 = DMC.SubModel(ThermalMass)
	m2 = DMC.SubModel(ThermalMass)
	c = DMC.SubModel(ThermalConduction)

	def __init__(self):
		self.m1.meta.T.connect(self.c.meta.T1)
		self.c.meta.QDot.connect(self.m1.meta.QDot)
		self.c.meta.QDot.connect(self.m2.meta.QDot)
		self.m2.meta.T.connect(self.c.meta.T2)
		self.createModelGraph()
		self.plotModelGraph()
	
		
if __name__ == '__main__':
	cir = ExampleCircuit()
	#cir = ThermalMass()