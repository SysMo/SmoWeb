'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
import StringIO
import networkx as nx
import pylab as plt
import numpy as np
from smo.web.exceptions import ConnectionError, FieldError
import SimulationActions as SA
from Fields import *

class DynamicalModelMeta(type):
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		
		# Collect fields from current class.
		dm_variables = []
		dm_submodels = []
		dm_realStates = []
		dm_functions = []
		for key, value in attrs.items():
			if isinstance(value, ScalarVariable):
				dm_variables.append((key, value))
				value.setName(key)
				attrs.pop(key)
				if (isinstance(value, RealState)):
					dm_realStates.append((key, value))
			elif isinstance(value, Function):
				dm_functions.append((key, value))
				value.setName(key)
				attrs.pop(key)
			elif isinstance(value, SubModel):
				dm_submodels.append((key, value))
				value.setName(key)
				attrs.pop(key)
		
		# Create special class variables with the collected fields
		dm_variables.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_variables'] = OrderedDict(dm_variables)
		dm_submodels.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_submodels'] = OrderedDict(dm_submodels)
		dm_realStates.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_realStates'] = OrderedDict(dm_realStates)
		dm_functions.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_functions'] = OrderedDict(dm_functions)
		
		new_class = (super(DynamicalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		return new_class

		
class InstanceMeta(object):
	def __init__(self):
		self.dm_variables = {}
		self.dm_submodels = {}
		self.dm_functions = {}
		
	def addInstanceVariable(self, instanceVariable):
		varName = instanceVariable.clsVar.name
		self.dm_variables[varName] = instanceVariable
		self.__setattr__(varName, instanceVariable)
		
	def addInstanceFunction(self, instanceFunction):
		funcName = instanceFunction.clsVar.name
		self.dm_functions[funcName] = instanceFunction
		self.__setattr__(funcName, instanceFunction)
		
class DynamicalModel(object):
	__metaclass__ = DynamicalModelMeta
	
	def __new__(cls, name = None, parent = None, *args, **kwargs):
		"""Constructor for all dynamical models. 
		Sets default values for all model fields"""
		self = object.__new__(cls)
		if (name is None):
			name = cls.__name__
		self.name = name
		self.parent = parent
		if (self.parent is not None):
			self.qPath = self.parent.qPath + [self.name]
		else:
			self.qPath = [self.name]
		# Create instance meta
		self.meta = InstanceMeta()
		# Create derivative vector
		self.der = DerivativeVector(self)
		# Create instance variables
		for name, clsVar in cls.dm_variables.iteritems():
			self.meta.addInstanceVariable(InstanceVariable(self, clsVar))
		# Create instance functions
		for name, clsVar in cls.dm_functions.iteritems():
			self.meta.addInstanceFunction(InstanceFunction(self, clsVar))
		# Create submodel instances
		for name, submodel in cls.dm_submodels.iteritems():
			instance = submodel.klass(name, self)
			self.__dict__[name] = instance
			self.meta.dm_submodels[name] = instance
			
		return self
	
	@property
	def qName(self):
		return '.'.join(self.qPath)
			
	def describeFields(self):
		buf = StringIO.StringIO()
		buf.write("=====================================\n")
		buf.write("Model: {}\n".format(self.__class__.__name__))
		buf.write("-------------------------------------\n")
		buf.write("Variables:\n")
		for k, v in self.__class__.dm_variables.iteritems():
			buf.write("\t{}: \n".format(k))
		buf.write("-------------------------------------\n")		
		buf.write("SubModels:\n")
		for k, v in self.meta.dm_submodels.iteritems():
			buf.write("{}: \n".format(k))
			buf.write(v.describeFields())
		buf.write("=====================================\n")
		result = buf.getvalue()
		buf.close()
		return result
	
	def createModelGraph(self, graph = None):
		if (graph is None):
			graph = nx.DiGraph()
			graph.add_node('stateVector')
			graph.add_node('stateDerivativeVector')
		else:
			graph.add_node(self)
		
		self.dm_graph = graph
		# Add all the variables 
		for k, v in self.meta.dm_variables.iteritems():
			if isinstance(v.clsVar, RealState):
				self.dm_graph.add_edge('stateVector', v)
				self.dm_graph.add_edge(v, self)
				self.dm_graph.add_edge(v.qName + '.der', 'stateDerivativeVector')
				self.dm_graph.add_edge(self, v.qName + '.der')
			if (v.clsVar.causality == Causality.Input):
				self.dm_graph.add_node(v)
				self.dm_graph.add_edge(v, self)
				if (len(v.connectedVars) > 0):
					self.dm_graph.add_edge(v.connectedVars[0], v)
			elif (v.clsVar.causality == Causality.Output):
				self.dm_graph.add_node(v)
				self.dm_graph.add_edge(self, v)
		# Insert functions and fix causality
		for k, v in self.meta.dm_functions.iteritems():
			self.dm_graph.add_node(v)
			for inVar in v.inputs:
				self.dm_graph.add_edge(inVar, v)
			for outVar in v.outputs:
				self.dm_graph.add_edge(v, outVar)
				self.dm_graph.remove_edge(self, outVar)
				self.dm_graph.add_edge(outVar, self)
				
		# Include recursively the submodels
		for k, v in self.__class__.dm_submodels.iteritems():
			self.__dict__[k].createModelGraph(graph)
				
	def plotModelGraph(self):
		#pos = nx.spring_layout(self.dm_graph)
		pos = nx.graphviz_layout(self.dm_graph, prog = 'neato', root = 'stateVector')
		posLabels = {}
		nx.draw_networkx_nodes(self.dm_graph, pos, node_size = 200, node_color='r',alpha=0.4)
		labels = {}
		for node in self.dm_graph.nodes_iter():
			posLabels[node] = pos[node] + np.array([0, -0.05])
			if (isinstance(node, basestring)):
				labels[node] = node 
			elif (isinstance(node, InstanceField)):
				labels[node] = node.qName
			elif (isinstance(node, DynamicalModel)):
				labels[node] = node.qName + '.compute'
		draw_networkx_labels(self.dm_graph, posLabels, labels, 
					horizontalalignment = 'left', rotation = 30.)
		nx.draw_networkx_edges(self.dm_graph, pos)
		plt.show()
		
	def generateSimulationSequence(self):
		if (self.dm_graph is None):
			self.createModelGraph()
		# Sequence of all actions in execution order
		self.simSequence = []
		# Sequence of functions to be called
		self.functionCallSequence = []
		# Set real states
		i = 0
		for state in self.dm_graph.successors('stateVector'):
			self.simSequence.append(SA.SetRealState(i, state))
			i += 1
			
		# Topological sort will return a node list with proper causality
		try:
			sortedGraph = nx.topological_sort(self.dm_graph)
		except nx.exception.NetworkXUnfeasible, e:
			raise RuntimeError("Cannot perfrom topological sort of the execution \
graph. Probably there are cyclic dependancies. \n \
Original error message: {}".format(e))
			
		for node in sortedGraph:
			if isinstance(node, DynamicalModel):
				self.simSequence.append(SA.CallMethod(node, 'compute'))
			elif isinstance(node, InstanceFunction):
				self.simSequence.append(SA.CallMethod(node.instance, node.name))
			elif isinstance(node, InstanceVariable):				
				pred = self.dm_graph.predecessors(node)
				if (len(pred) > 0):
					pred = pred[0]
					if (isinstance(pred, InstanceVariable)):
						self.simSequence.append(SA.AssignValue(pred, node))
				else:
					print("Warning variable {.qName} receives no value".format(node))
		# Get real derivatives
		i = 0
		for state in self.dm_graph.successors('stateVector'):
			self.simSequence.append(SA.GetRealStateDerivative(i, state))
			i += 1
	
	def printSimulationSequence(self):
		for action in self.simSequence:
			print action
			
def draw_networkx_labels(G, pos,
						 labels=None,
						 font_size=12,
						 font_color='k',
						 font_family='sans-serif',
						 font_weight='normal',
						 alpha=1.0,
						 ax=None,
						 **kwds):
	try:
		import matplotlib.pyplot as plt
		import matplotlib.cbook as cb
	except ImportError:
		raise ImportError("Matplotlib required for draw()")
	except RuntimeError:
		print("Matplotlib unable to open display")
		raise

	if ax is None:
		ax = plt.gca()

	if labels is None:
		labels = dict((n, n) for n in G.nodes())

	# set optional alignment
	horizontalalignment = kwds.get('horizontalalignment', 'center')
	verticalalignment = kwds.get('verticalalignment', 'center')
	rotation = kwds.get('rotation', 0)
	text_items = {}  # there is no text collection so we'll fake one
	for n, label in labels.items():
		(x, y) = pos[n]
		if not cb.is_string_like(label):
			label = str(label)  # this will cause "1" and 1 to be labeled the same
		t = ax.text(x, y,
				  label,
				  size=font_size,
				  color=font_color,
				  family=font_family,
				  weight=font_weight,
				  horizontalalignment=horizontalalignment,
				  verticalalignment=verticalalignment,
				  transform=ax.transData,
				  clip_on=True,
				  rotation = rotation
				  )
		text_items[n] = t

	return text_items
