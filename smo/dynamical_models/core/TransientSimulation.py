'''
Created on May 25, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from assimulo.solvers import CVode
from assimulo.problem import Explicit_Problem
import numpy as np
import SimulationActions as SA
from SimulationCompiler import SimulationCompiler 

class TransientSimulation(Explicit_Problem):
	def __init__(self, model):
		self.model = model
		
	def setUp(self):
		"""
		Configures the solver
		"""
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

	def initializeModel(self):
		self.compiler = SimulationCompiler(self.model)
		self.compiler.createModelGraph()
		self.compiler.generateSimulationSequence()
		#model.simCmpl.printSimulationSequence()
		#model.simCmpl.plotDependencyGraph()
		numRealStates = len(self.compiler.realStates)

		# Run initializing functions
		self.model.recursiveInitialize()

		# Initialize state vector
		self.y0 = np.zeros(numRealStates)
		i = 0
		for state in self.compiler.realStates:
			self.y0[i] = state.getValue()
			i += 1
		print ("Initial values: {}".format(self.y0))
		
		# Create vector for storing state derivatives
		self.yDot = np.zeros(numRealStates)
		
		# Configure solver
		self.setUp()

	def computeDerivatives(self, t, stateVector, stateDerivatives):
		"""
		Execute the simulation sequence to compute derivatives
		"""		
		for action in self.compiler.actionSequence:
			if isinstance(action , SA.SetRealState):
				action.execute(stateVector)
			elif isinstance(action, SA.GetRealStateDerivative):
				action.execute(stateDerivatives)
			elif isinstance(action, SA.CallMethod):
				action.execute(t)
			else:
				action.execute()

	def rhs(self, t, y):
		"""
		Callback method for the Assimulo solver to compute derivatives
		"""
		try:
			self.computeDerivatives(t, y, self.yDot)
		except Exception, e:
			# Log the error if it happens in the compute() function
			print('Exception at time {}: {}'.format(t, e))
			raise e
		return self.yDot
	
	def run(self, tFinal, tPrint):
		"""
		Runs the transient simulation
		"""
		import math
		# Remember the final time
		self.tFinal = tFinal
		
		# Run simulation		
		self.result = self.simSolver.simulate(
			tfinal = tFinal, 
			ncp = math.floor(tFinal/tPrint)
		)
				