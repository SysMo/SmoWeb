'''
Created on May 3, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.dynamical_models.core.DynamicalModel import DynamicalModel
from smo.dynamical_models.core.Fields import Variability as VR, Causality as CS
import smo.dynamical_models.core.Fields as F 
from smo.web.exceptions import ConnectionError
import numpy as np

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
	m = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 10.)
	cp = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 100.)
	T = F.RealState(start = 300)
	QDot1 = F.RealVariable(causality = CS.Input)
	QDot2 = F.RealVariable(causality = CS.Input)
	p1 = ThermalPort('C', TVar = T, QVar = QDot1)
	p2 = ThermalPort('C', TVar = T, QVar = QDot2)
	
	def compute(self):
		self.der.T = (self.QDot1 + self.QDot2) / self.m / self.cp 

class ThermalConduction(DynamicalModel):
	k = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 1)
	T1 = F.RealVariable(causality = CS.Input)
	QDot1 = F.RealVariable(causality = CS.Output)
	T2 = F.RealVariable(causality = CS.Input)
	QDot2 = F.RealVariable(causality = CS.Output)
	p1 = ThermalPort('R', TVar = T1, QVar = QDot1)
	p2 = ThermalPort('R', TVar = T2, QVar = QDot2)

	def compute(self):
		self.QDot1 = self.k * (self.T2 - self.T1)
		self.QDot2 = - self.QDot1
		
class Convection(DynamicalModel):
	hConv = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 10)
	area = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 0.2)
	pFluid = F.RealVariable(causality = CS.Input)
	TFluid = F.RealVariable(causality = CS.Input)
	TWall = F.RealVariable(causality = CS.Input)
	QFluid = F.RealVariable(causality = CS.Output)
	QWall = F.RealVariable(causality = CS.Output)
	portFluid = F.Port([pFluid, TFluid, QFluid])
	portWall = ThermalPort('R', TVar = TWall, QVar = QWall)
	
	def compute(self):
		self.QFluid = self.hConv * self.area * (self.TWall - self.TFluid)
		self.QWall = -self.QFluid

class FluidChamber(DynamicalModel):
	VFluid = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 0.1)
	T = F.RealState(start = 300)
	rho = F.RealState(start = 1)
	p = F.RealVariable(causality = CS.Output)
	m = F.RealVariable(causality = CS.Output)
	QDotWall = F.RealVariable(causality = CS.Input)
	portWall = F.Port([p, T, QDotWall])

	@F.Function(inputs = [T, rho], outputs = [p])
	def setState(self):
		RGas = 8.13 / 2e-3
		self.p = RGas * self.rho * self.T

	def compute(self):
		RGas = 8.13 / 2e-3
		self.m = self.VFluid * self.rho
		self.der.rho = 0
		self.der.T = self.QDotWall / self.m / (5./2 * RGas)


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
			
	def test(self): 
		#print self.describeFields()
		x = np.zeros(self.simCmpl.numRealStates)
		x[:] = [200, 15, 300, 300]
		xDot = np.zeros(self.simCmpl.numRealStates)
		self.computeDerivatives(x, xDot)
		print x
		print xDot

from assimulo.solvers import CVode
from assimulo.problem import Explicit_Problem

class TransientSimulation(Explicit_Problem):
	def __init__(self, model):
		self.model = model
		model.simCmpl.createModelGraph()
		model.simCmpl.generateSimulationSequence()
		#model.simCmpl.printSimulationSequence()
		#model.simCmpl.plotDependencyGraph()
		
		self.y0 = np.zeros(model.simCmpl.numRealStates)
		self.y0[:] = [200, 15, 300, 300]
		self.yDot = np.zeros(model.simCmpl.numRealStates)

	def rhs(self, t, y):
		try:
			self.model.computeDerivatives(y, self.yDot)
		except Exception, e:
			# Log the error if it happens in the compute() function
			print('Exception at time {}: {}'.format(t, e))
			raise e
		return self.yDot
	
	def prepareSimulation(self):
		#Define an explicit solver 
		simSolver = CVode(self) 
		#Create a CVode solver
		#Sets the parameters 
		#simSolver.verbosity = LOUD
		#simSolver.report_continuously = True
		simSolver.iter = 'Newton' #Default 'FixedPoint'
		simSolver.discr = 'BDF' #Default 'Adams'
		#simSolver.discr = 'Adams' 
		simSolver.atol = [1e-6]	#Default 1e-6 
		simSolver.rtol = 1e-6 	#Default 1e-6
		#simSolver.problem_info['step_events'] = True # activates step events
		#simSolver.maxh = 1.0
		#simSolver.store_event_points = True
		self.simSolver = simSolver
		
	def run(self, tFinal, tPrint):
		import math
		# Remember the final time
		self.tFinal = tFinal
		
		# Run simulation		
		self.result = self.simSolver.simulate(
			tfinal = tFinal, 
			ncp = math.floor(tFinal/tPrint)
		)
				

if __name__ == '__main__':
	cir = ExampleCircuit()
	sim = TransientSimulation(cir)
	sim.prepareSimulation()
	sim.run(tFinal = 10000., tPrint = 10.)
	t = sim.result[0]
	T = sim.result[1][:, [0, 2, 3]]
	import pylab as plt
	plt.plot(t, T)
	plt.show()
