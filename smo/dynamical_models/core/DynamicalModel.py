'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
import StringIO
from smo.web.exceptions import ConnectionError, FieldError

class Causality(object):
	Parameter = 0
	CalculatedParameter = 1
	Input = 2
	Output = 3
	Local = 4
	Independent = 5
	RealState = 6
	TimeDerivative = 7
	
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
	def __init__(self, start, **kwargs):
		super(RealState, self).__init__(causality = Causality.RealState, 
				variability = Variability.Continuous, **kwargs)
		self.start = start
		
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
		dm_realStates = []
		for key, value in attrs.items():
			if isinstance(value, ScalarVariable):
				dm_variables.append((key, value))
				value.setName(key)
				attrs.pop(key)
				if (isinstance(value, RealState)):
					dm_realStates.append((key, value))
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
		
		new_class = (super(DynamicalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		return new_class

class DerivativeVector(object):
	def __init__(self, model):
		object.__setattr__(self, 'model', model)
		object.__setattr__(self, 'dm_realStates', model.__class__.dm_realStates)
		for name in self.dm_realStates.keys():
			object.__setattr__(self, name, 0)
	
	def __setattr__(self, name, value):
		if (name in self.dm_realStates.keys()):			
			object.__setattr__(self, name, value)
		else:
			raise FieldError('No state derivative with name {}'.format(name))
		
class InstanceVariable(object):
	def __init__(self, instance, clsVar):
		self.instance = instance
		self.clsVar = clsVar
		self.connectedVars = []
		
	@property
	def name(self):
		return self.clsVar.name
	@property
	def qPath(self):
		return self.instance.qPath + [self.name]
	@property
	def qName(self):
		return '.'.join(self.qPath)
	
	def connect(self, other, complement = True):
		# Input variables
		if (self.clsVar.causality == Causality.Input):
			if (len(self.connectedVars) != 0):
				raise ConnectionError(self, other, 'Cannot connect input to more than one variable')
			elif (other.clsVar.causality == Causality.Output or other.clsVar.causality == Causality.RealState):
				self.connectedVars.append(other)
				if (complement):
					other.connect(self, complement = False)
			else:
				raise ConnectionError(self, other, 'Can only connect Input variable to an Output variable or RealState')
		
		# Output variables
		elif (self.clsVar.causality == Causality.Output):
			if (other.clsVar.causality == Causality.Input):
				if(other not in self.connectedVars):
					self.connectedVars.append(other)
					if (complement):
						other.connect(self, complement = False)
				else:
					pass
			else:
				raise ConnectionError(self, other, 'Can only connect Output variable to an Input variable')
		
		# State variables
		elif (self.clsVar.causality == Causality.RealState):
			if (other.clsVar.causality == Causality.Input):
				if(other not in self.connectedVars):
					self.connectedVars.append(other)
					if (complement):
						other.connect(self, complement = False)
				else:
					pass
			else:
				raise ConnectionError(self, other, 'Can only connect RealState variable to an input variable')

		# Other
		else:
			raise ConnectionError(self, other, 'Connected variables must have causality Input, Output or RealState')
		
class InstanceMeta(object):
	def __init__(self):
		self.dm_variables = {}
		self.dm_submodels = {}
		
	def addInstanceVariable(self, instanceVariable):
		varName = instanceVariable.clsVar.name
		self.dm_variables[varName] = instanceVariable
		self.__setattr__(varName, instanceVariable)
		
		
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
		import networkx as nx
		if (graph is None):
			graph = nx.DiGraph()
			graph.add_node('stateVector')
			graph.add_node('stateDerivativeVector')
		else:
			graph.add_node(self)
		
		self.dm_graph = graph 
		for k, v in self.meta.dm_variables.iteritems():
			if isinstance(v.clsVar, RealState):
				self.dm_graph.add_edge('stateVector', v)
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
		for k, v in self.__class__.dm_submodels.iteritems():
			self.__dict__[k].createModelGraph(graph)
				
	def plotModelGraph(self):
		import networkx as nx
		import pylab as plt
		import numpy as np
		#pos = nx.spring_layout(self.dm_graph)
		pos = nx.graphviz_layout(self.dm_graph, prog = 'neato', root = 'stateVector')
		posLabels = {}
		nx.draw_networkx_nodes(self.dm_graph, pos, node_size = 100)
		labels = {}
		for node in self.dm_graph.nodes_iter():
			posLabels[node] = pos[node] + np.array([0, -0.05])
			if (isinstance(node, basestring)):
				labels[node] = node 
			elif (isinstance(node, InstanceVariable)):
				labels[node] = node.qName
			elif (isinstance(node, DynamicalModel)):
				labels[node] = node.qName + '.compute'
		nx.draw_networkx_labels(self.dm_graph, posLabels, labels)
		nx.draw_networkx_edges(self.dm_graph, pos)
		plt.show()
		