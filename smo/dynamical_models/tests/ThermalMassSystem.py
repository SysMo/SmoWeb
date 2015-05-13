'''
Created on May 3, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.dynamical_models.core.DynamicalModel import DynamicalModel
from smo.dynamical_models.core.Fields import Variability as VR, Causality as CS
import smo.dynamical_models.core.Fields as F 
from smo.web.exceptions import ConnectionError
#import networkx as nx

class ThermalPort(F.Port):
	def __init__(self, subType, TVar, QVar):
		super(ThermalPort, self).__init__([TVar, QVar], subType)
	def checkConnect(self, other):
		if (isinstance(other, ThermalPort)):
			if (self.subType == 'R' and other.subType == 'C'):
				return True
			elif (self.subType == 'C' and other.subType == 'R'):
				return True
			else:
				raise ConnectionError('Only complementary ports can be connected')
		else:
			raise ConnectionError('Incompatible port types')

class ThermalMass(DynamicalModel):
	m = F.RealVariable(causality = CS.Parameter, variability = VR.Constant)
	T = F.RealState(start = 300)	
	QDot1 = F.RealVariable(causality = CS.Input)
	QDot2 = F.RealVariable(causality = CS.Input)
	p1 = ThermalPort('C', TVar = T, QVar = QDot1)
	p2 = ThermalPort('C', TVar = T, QVar = QDot2)
	

class ThermalConduction(DynamicalModel):
	k = F.RealVariable(causality = CS.Parameter, variability = VR.Constant)
	T1 = F.RealVariable(causality = CS.Input)
	QDot1 = F.RealVariable(causality = CS.Output)
	T2 = F.RealVariable(causality = CS.Input)
	QDot2 = F.RealVariable(causality = CS.Output)
	p1 = ThermalPort('R', TVar = T1, QVar = QDot1)
	p2 = ThermalPort('R', TVar = T2, QVar = QDot2)

class FluidChamber(DynamicalModel):
	VFluid = F.RealVariable(causality = CS.Parameter)
	T = F.RealState(start = 300)
	rho = F.RealState(start = 1)
	p = F.RealVariable(causality = CS.Output)
	m = F.RealVariable(causality = CS.Output)
	QDotWall = F.RealVariable(causality = CS.Input)
	portWall = F.Port([p, T, QDotWall])
	setState = F.Function(inputs = [T, rho], outputs = [p])

class Convection(DynamicalModel):
	pFluid = F.RealVariable(causality = CS.Input)
	TFluid = F.RealVariable(causality = CS.Input)
	TWall = F.RealVariable(causality = CS.Input)
	QFluid = F.RealVariable(causality = CS.Output)
	QWall = F.RealVariable(causality = CS.Output)
	portFluid = F.Port([pFluid, TFluid, QFluid])
	portWall = ThermalPort('R', TVar = TWall, QVar = QWall)

class ExampleCircuit(DynamicalModel):
	m1 = F.SubModel(ThermalMass)
	m2 = F.SubModel(ThermalMass)
	c = F.SubModel(ThermalConduction)
	conv = F.SubModel(Convection)
	ch = F.SubModel(FluidChamber)

	def __init__(self):
		#self.m1.meta.T.connect(self.c.meta.T1)
		#self.m1.meta.QDot2.connect(self.c.meta.QDot1)
		self.m1.meta.p2.connect(self.c.meta.p1)
		self.c.meta.p2.connect(self.m2.meta.p1)
		self.m2.meta.p2.connect(self.conv.meta.portWall)
		self.ch.meta.portWall.connect(self.conv.meta.portFluid)
		
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