'''
Created on May 22, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import networkx as nx
import pylab as plt
#from smo.web.exceptions import ConnectionError, FieldError
import Fields as F
import numpy as np
from DynamicalModel import DynamicalModel
import SimulationActions as SA

class SimulationCompiler(object):
	"""
	Object generating and executing the simulation
	Attributes:
	
		* :attr:`depGraph`: 
		* :attr:`actionSequence`: 
		* :attr:`numRealStates`: 
		* :attr:``: 
	"""
	def __init__(self, model):
		self.model = model
		
	def createModelGraph(self, model = None):
		"""
		Builds dependancy graph for all variables and functions in the model
		"""
		self.depGraph = nx.DiGraph()
		self.depGraph.add_node('stateVector')
		self.depGraph.add_node('stateDerivativeVector')
		self.addModelToDependencyGraph(self.model)
		self.realStates = self.depGraph.successors('stateVector')
		print("Real states ({}): [{}]".format(len(self.realStates), ", ".join(state.qName for state in self.realStates)))
	
	def addModelToDependencyGraph(self, model):
		self.depGraph.add_node(model)
		# Add all the variables 
		for k, v in model.meta.dm_variables.iteritems():
			if isinstance(v.clsVar, F.RealState):
				self.depGraph.add_edge('stateVector', v)
				self.depGraph.add_edge(v, model)
				self.depGraph.add_edge(v.qName + '.der', 'stateDerivativeVector')
				self.depGraph.add_edge(model, v.qName + '.der')
			if (v.clsVar.causality == F.Causality.Input):
				self.depGraph.add_node(v)
				self.depGraph.add_edge(v, model)
				if (len(v.connectedVars) > 0):
					self.depGraph.add_edge(v.connectedVars[0], v)
			elif (v.clsVar.causality == F.Causality.Output):
				self.depGraph.add_node(v)
				self.depGraph.add_edge(model, v)
		# Insert functions and fix causality
		for k, v in model.meta.dm_functions.iteritems():
			self.depGraph.add_node(v)
			for inVar in v.inputs:
				self.depGraph.add_edge(inVar, v)
			for outVar in v.outputs:
				self.depGraph.add_edge(v, outVar)
				self.depGraph.remove_edge(model, outVar)
				self.depGraph.add_edge(outVar, model)
				
		# Include recursively the submodels
		for subModelName in model.__class__.dm_submodels.iterkeys():
			self.addModelToDependencyGraph(getattr(model, subModelName))
	
	def plotDependencyGraph(self):
		"""
		Plots the model graph of dependencies 
		"""
		#pos = nx.spring_layout(graph)
		from smo.dynamical_models.Utils import draw_networkx_labels
		pos = nx.graphviz_layout(self.depGraph, prog = 'neato', root = 'stateVector')
		posLabels = {}
		labels = {}
		colors = np.zeros(shape = (len(self.depGraph.nodes())), dtype = 'S')
		colors.fill('r')
		# Assign colors and labels to nodes
		i = 0
		for node in self.depGraph.nodes_iter():
			posLabels[node] = pos[node] + np.array([0, -0.05])
			if (isinstance(node, basestring)):
				labels[node] = node
			elif (isinstance(node, F.InstanceVariable)):
				labels[node] = node.qName
				colors[i] = 'b'
			elif (isinstance(node, F.InstanceFunction)):
				labels[node] = node.qName
				colors[i] = 'g'
			elif (isinstance(node, DynamicalModel)):
				labels[node] = node.qName + '.compute'
				colors[i] = 'g'
			i += 1

		# Draw nodes
		nx.draw_networkx_nodes(self.depGraph, 
				pos, node_size = 200, node_color= colors, alpha=0.5)
		# Draw edges
		nx.draw_networkx_edges(self.depGraph, pos)
		# Draw labels
		draw_networkx_labels(self.depGraph, posLabels, labels, 
				horizontalalignment = 'left', rotation = 30.)
		plt.show()
		
	def generateSimulationSequence(self):
		"""
		Creates a simulation sequence using the information in the model graph
		"""
		if (self.depGraph is None):
			self.createModelGraph()
		# Sequence of all actions in execution order
		self.actionSequence = []
		# Set real states
		i = 0
		for state in self.depGraph.successors('stateVector'):
			self.actionSequence.append(SA.SetRealState(i, state))
			i += 1
			
		# Topological sort will return a node list with proper causality
		try:
			sortedGraph = nx.topological_sort(self.depGraph)
		except nx.exception.NetworkXUnfeasible, e:
			raise RuntimeError("Cannot perform topological sort of the execution \
graph. Probably there are cyclic dependencies. \n \
Original error message: {}".format(e))
			
		for node in sortedGraph:
			if isinstance(node, DynamicalModel):
				self.actionSequence.append(SA.CallMethod(node, 'compute'))
			elif isinstance(node, F.InstanceFunction):
				self.actionSequence.append(SA.CallMethod(node.modelInstance, node.name))
			elif isinstance(node, F.InstanceVariable):				
				pred = self.depGraph.predecessors(node)
				if (len(pred) > 0):
					pred = pred[0]
					if (isinstance(pred, F.InstanceVariable)):
						self.actionSequence.append(SA.AssignValue(pred, node))
				else:
					print("Warning variable {.qName} receives no value".format(node))
		# Get real derivatives
		i = 0
		for state in self.depGraph.successors('stateVector'):
			self.actionSequence.append(SA.GetRealStateDerivative(i, state))
			i += 1
	
	def printSimulationSequence(self):
		"""
		Prints the simulation sequence
		"""
		for action in self.actionSequence:
			print action