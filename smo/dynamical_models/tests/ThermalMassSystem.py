'''
Created on May 3, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.dynamical_models.core as DMC
from smo.dynamical_models.core import Causality as C
from smo.dynamical_models.core import Variability as V
#import networkx as nx

class ThermalMass(DMC.DynamicalModel):
	m = DMC.RealVariable(causality = C.Parameter, variability = V.Constant)
	T = DMC.RealState(start = 300)
	QDot1 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	QDot2 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)

class ThermalConduction(DMC.DynamicalModel):
	k = DMC.RealVariable(causality = C.Parameter, variability = V.Constant)
	T1 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	T2 = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	QDot1 = DMC.RealVariable(causality = C.Output, variability = V.Continuous)
	QDot2 = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class FluidChamber(DMC.DynamicalModel):
	VFluid = DMC.RealVariable(causality = C.Parameter, variability = V.Constant)
	T = DMC.RealState(start = 300)
	rho = DMC.RealState(start = 1)
	p = DMC.RealVariable(causality = C.Output, variability = V.Continuous)
	m = DMC.RealVariable(causality = C.Output, variability = V.Continuous)
	QDotWall = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	setState = DMC.Function(inputs = [T, rho], outputs = [p])

class Convection(DMC.DynamicalModel):
	pFluid = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	TFluid = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	TWall = DMC.RealVariable(causality = C.Input, variability = V.Continuous)
	QFluid = DMC.RealVariable(causality = C.Output, variability = V.Continuous)
	QWall = DMC.RealVariable(causality = C.Output, variability = V.Continuous)

class ExampleCircuit(DMC.DynamicalModel):
	m1 = DMC.SubModel(ThermalMass)
	m2 = DMC.SubModel(ThermalMass)
	c = DMC.SubModel(ThermalConduction)
	conv = DMC.SubModel(Convection)
	ch = DMC.SubModel(FluidChamber)

	def __init__(self):
		self.m1.meta.T.connect(self.c.meta.T1)
		self.m1.meta.QDot2.connect(self.c.meta.QDot1)
		self.m2.meta.T.connect(self.c.meta.T2)
		self.m2.meta.QDot1.connect(self.c.meta.QDot2)
		self.m2.meta.T.connect(self.conv.meta.TWall)
		self.m2.meta.QDot2.connect(self.conv.meta.QWall)
		self.ch.meta.T.connect(self.conv.meta.TFluid)
		self.ch.meta.p.connect(self.conv.meta.pFluid)
		self.ch.meta.QDotWall.connect(self.conv.meta.QFluid)
		
		#print self.describeFields()
		self.createModelGraph()
		self.generateSimulationSequence()
		self.printSimulationSequence()
		self.plotModelGraph()
		
if __name__ == '__main__':
	cir = ExampleCircuit()
	#print dir(cir.der)
	#print cir.m1.der.T
	#cir = ThermalMass()