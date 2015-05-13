'''
Created on May 10, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
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
	
class Function(ModelField):
	def __init__(self, inputs, outputs, **kwargs):
		super(Function, self).__init__(**kwargs)
		self.inputs = inputs
		self.outputs = outputs
		# TODO: check causalities

class Port(ModelField):
	def __init__(self, variables, subType = None, **kwargs):
		super(Port, self).__init__(**kwargs)
		self.variables = variables		
		self.subType = subType		
	def checkConnect(self, other):
		if (len(self.variables) != len(other.variables)):
			raise ConnectionError('Cannot connect ports with different number of variables')
	
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
	def __init__(self, causality = Causality.Local, variability = Variability.Continuous, **kwargs):
		super(RealVariable, self).__init__(causality, variability, **kwargs)

class RealState(RealVariable):
	def __init__(self, start, **kwargs):
		super(RealState, self).__init__(causality = Causality.RealState, 
				variability = Variability.Continuous, **kwargs)
		self.start = start
		
class SubModel(ModelField):
	def __init__(self, klass, **kwargs):
		super(SubModel, self).__init__(**kwargs)
		self.klass = klass

class InstanceField(object):
	def __init__(self, instance, clsVar):
		self.instance = instance
		self.clsVar = clsVar
	@property
	def name(self):
		return self.clsVar.name
	@property
	def qPath(self):
		return self.instance.qPath + [self.name]
	@property
	def qName(self):
		return '.'.join(self.qPath)

class InstanceVariable(InstanceField):
	def __init__(self, instance, clsVar):
		super(InstanceVariable, self).__init__(instance, clsVar)
		self.connectedVars = []
	def connect(self, other, complement = True):
		# Input variables
		if (self.clsVar.causality == Causality.Input):
			if (len(self.connectedVars) != 0):
				raise ConnectionError(self, other, 'Cannot connect input {.qName} to more than one variable'.format(self))
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

class InstanceFunction(InstanceField):
	def __init__(self, instance, clsVar):
		super(InstanceFunction, self).__init__(instance, clsVar)
		self.inputs = []
		self.outputs = []
		for inVar in clsVar.inputs:
			self.inputs.append(instance.meta.dm_variables[inVar.name])
		for outVar in clsVar.outputs:
			self.outputs.append(instance.meta.dm_variables[outVar.name])

class InstancePort(InstanceField):
	def __init__(self, instance, clsVar):
		super(InstancePort, self).__init__(instance, clsVar)
		self.variables = []
		for var in clsVar.variables:
			self.variables.append(instance.meta.dm_variables[var.name])
	
	def connect(self, other):
		self.clsVar.checkConnect(other.clsVar)
		for (thisVar, otherVar) in zip(self.variables, other.variables):
			thisVar.connect(otherVar)

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
