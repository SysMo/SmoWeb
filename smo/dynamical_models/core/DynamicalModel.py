'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
import StringIO

class Causality(object):
	Parameter = 0
	CalculatedParameter = 1
	Input = 2
	Output = 3
	Local = 4
	Independent = 5
	
class Variability(object):
	Constant = 0
	Fixed = 1
	Tunable = 2
	Discrete = 3
	Continuous = 4

class ModelField(object):
	"""
	Abstract base class for all the field types.
	"""
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	def __init__(self, label = None, description = None):
		self.label = label
		self.description = description

		# Increase the creation counter, and save our local copy.
		self.creation_counter = ModelField.creation_counter
		ModelField.creation_counter += 1

	def setName(self, name):
		self.name = name
		if (self.label is None):
			self.label = self.name
		if (self.description is None):
			self.description = self.label
	

class ScalarVariable(ModelField):
	def __init__(self, causality, variability, **kwargs):
		"""
	 	:param str label: the text label used in the user interface usually in front of the field
	 	:param str description: description to show as tooltip when hovering over the field label
		"""
		super(ScalarVariable, self).__init__(**kwargs)
		self.causality = causality
		self.variability = variability

class RealVariable(ScalarVariable):
	def __init__(self, **kwargs):
		super(RealVariable, self).__init__(**kwargs)

class RealState(RealVariable):
	def __init__(self, **kwargs):
		super(RealState, self).__init__(**kwargs)

class SubModel(ModelField):
	def __init__(self, klass, **kwargs):
		super(SubModel, self).__init__(**kwargs)
		self.klass = klass

class DynamicalModelMeta(type):
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		
		# Collect fields from current class.
		dm_variables = []
		dm_submodels = []
		for key, value in attrs.items():
			if isinstance(value, ScalarVariable):
				dm_variables.append((key, value))
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
		
		new_class = (super(DynamicalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		return new_class
	
class DynamicalModel(object):
	__metaclass__ = DynamicalModelMeta
	
	def __new__(cls, *args, **kwargs):
		"""Constructor for all dynamical models. 
		Sets default values for all model fields"""
		self = object.__new__(cls)
		self.name = cls.__name__
		for name, submodel in cls.dm_submodels.iteritems():
			instance = submodel.klass()
			instance.name = name
			self.__dict__[name] = instance
			
		return self
	
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
		for k, v in self.__class__.dm_submodels.iteritems():
			buf.write("{}: \n".format(k))
		buf.write("=====================================\n")
		result = buf.getvalue()
		buf.close()
		return result
	
	def createModelGraph(self, graph = None):
		import networkx as nx
		if (graph is None):
			graph = nx.DiGraph()
		self.dm_graph = graph 
		self.dm_graph.add_node(self)
		for k, v in self.__class__.dm_variables.iteritems():
			if (v.causality == Causality.Input):
				self.dm_graph.add_node(v)
				self.dm_graph.add_edge(v, self)
			elif (v.causality == Causality.Output):
				self.dm_graph.add_node(v)
				self.dm_graph.add_edge(self, v)
		for k, v in self.__class__.dm_submodels.iteritems():
			self.__dict__[k].createModelGraph(graph)
				
	def plotModelGraph(self):
		import networkx as nx
		import pylab as plt
		import numpy as np
		pos = nx.spring_layout(self.dm_graph)
		posLabels = {}
		nx.draw_networkx_nodes(self.dm_graph, pos, node_size = 100)
		labels = {}
		for node in self.dm_graph.nodes_iter():
			posLabels[node] = pos[node] + np.array([0, -0.05])
			if (isinstance(node, ScalarVariable)):
				labels[node] = node.name
			else:
				labels[node] = node.name
		nx.draw_networkx_labels(self.dm_graph, posLabels, labels)
		nx.draw_networkx_edges(self.dm_graph, pos)
		print pos
		plt.show()
				
	def connect(self, n1, n2):
		self.dm_graph.add_edge(n1, n2)
		