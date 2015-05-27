'''
Created on May 10, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.web.exceptions import ConnectionError, FieldError

class Causality(object):
	"""
	Defines information direction for the variable
	"""
	Parameter = 0
	CalculatedParameter = 1
	Input = 2
	Output = 3
	Local = 4
	Independent = 5
	RealState = 6
	#TimeDerivative = 7
	
class Variability(object):
	"""
	Defines the variability of a variable
	"""
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
		"""
	 	:param str label: text
	 	:param str description: verboose description
		"""
		self.label = label
		self.description = description

		# Increase the creation counter, and save our local copy.
		self.creation_counter = ModelField.creation_counter
		ModelField.creation_counter += 1

	def setName(self, name):
		"""		
		This method is explicitly called to set the field name

		:param name: field name
		
		"""
		self.name = name
		if (self.label is None):
			self.label = self.name
		if (self.description is None):
			self.description = self.label
	
class Function(ModelField):
	"""
	Represents a calculation function in the model
	"""
	def __init__(self, inputs, outputs, **kwargs):
		"""
		:param inputs: input variable list
		:param outputs: output variable list
		"""
		super(Function, self).__init__(**kwargs)
		self.inputs = inputs
		self.outputs = outputs
		# TODO: check causalities
	
	def __call__(self, funcDef):
		self.funcDef = funcDef
		return self

class Port(ModelField):
	"""
	Port is a group of model variables exposed to the external world, 
	used to connect to other models
	"""
	def __init__(self, variables, subType = None, **kwargs):
		'''
		:param variables: list of the port variables 
		:param subtype: derived classes can define special subtypes (e.g. C-port or R-port) 
		'''
		super(Port, self).__init__(**kwargs)
		self.variables = variables		
		self.subType = subType		
	
	def checkConnect(self, other):		
		'''
		Perform basic check whether this port can be connected to the other one. Currently it checks:
		
		 * the two ports have the same number of variables 
		
		:param other: other port that this one is connected to
		:type other: :class:`Port`
		'''
		if (len(self.variables) != len(other.variables)):
			raise ConnectionError('Cannot connect ports with different number of variables')
	
class ScalarVariable(ModelField):
	"""
	A fundamental variable field for the model 
	"""
	def __init__(self, causality, variability, **kwargs):
		"""
	 	:param causality: causality
	 	:param variabilty: variability
		"""
		super(ScalarVariable, self).__init__(**kwargs)
		self.causality = causality
		self.variability = variability
	
	@property
	def default(self):
		raise NotImplementedError("{} does not implement 'default' property".format(self.__class__))
	
class RealVariable(ScalarVariable):
	"""
	Scalar variable of type real
	"""
	def __init__(self, causality = Causality.Local, variability = Variability.Continuous, default = 0., **kwargs):
		super(RealVariable, self).__init__(causality, variability, **kwargs)
		self.defaultValue = float(default)
		
	@property
	def default(self):
		return self.defaultValue

class RealState(RealVariable):
	"""
	Real variable which is continuous state. Its value cannot be set directly
	by the model, but rather its derivative is calculated and then passed to 
	the integrator, which computes the value over time.   
	"""
	def __init__(self, start, **kwargs):
		
		super(RealState, self).__init__(causality = Causality.RealState, 
				variability = Variability.Continuous, **kwargs)
		self.start = start

	@property
	def default(self):
		return self.start
		
class IntegerVariable(ScalarVariable):
	"""
	Scalar variable of type integer
	"""
	def __init__(self, causality = Causality.Local, variability = Variability.Discrete, default = 0, **kwargs):
		super(IntegerVariable, self).__init__(causality, variability, **kwargs)
		self.defaultValue = int(default)
		
	@property
	def default(self):
		return self.defaultValue
	

class StateEvent(ModelField):
	"""
	"""
	def __init__(self, locate, **kwargs):
		super(StateEvent, self).__init__(**kwargs)
		self.locate = locate
		
	def __call__(self, update):
		self.update = update
		return self

class SubModel(ModelField):
	"""
	Submodel as part of a larger model
	"""
	def __init__(self, klass, **kwargs):
		"""
		:param klass: submodel class (must be subclass of :class:`DynamicalModel`)
		"""
		super(SubModel, self).__init__(**kwargs)
		self.klass = klass

class InstanceField(object):
	"""
	An abstract base class for a field in a :class:`DynamicalModel` instance, 
	corresponding to a field in the	model definition.
	"""
	def __init__(self, modelInstance, clsVar):
		"""
		:param modelInstance: dynamical model instance
		:param clsVar: class variable corresponding to this instance variable
		  defined in the dynamical model
		"""
		self.modelInstance = modelInstance
		self.clsVar = clsVar
	@property
	def name(self):
		""""""
		return self.clsVar.name
	@property
	def qPath(self):
		""""""
		return self.modelInstance.qPath + [self.name]
	@property
	def qName(self):
		""""""
		return '.'.join(self.qPath)

class InstanceVariable(InstanceField):
	"""
	Variable in a model instance
	"""
	def __init__(self, **kwargs):
		super(InstanceVariable, self).__init__(**kwargs)
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
	
	def setValue(self, value):
		setattr(self.modelInstance, self.clsVar.name, value)
		
	def getValue(self):
		return getattr(self.modelInstance, self.clsVar.name)

class InstanceFunction(InstanceField):
	"""
	Function in a model instance
	"""
	def __init__(self, **kwargs):
		super(InstanceFunction, self).__init__(**kwargs)
		self.inputs = []
		self.outputs = []
		for inVar in self.clsVar.inputs:
			self.inputs.append(self.modelInstance.meta.dm_variables[inVar.name])
		for outVar in self.clsVar.outputs:
			self.outputs.append(self.modelInstance.meta.dm_variables[outVar.name])
	

class InstancePort(InstanceField):
	"""
	Port in a model instance
	"""
	def __init__(self, **kwargs):
		super(InstancePort, self).__init__(**kwargs)
		self.variables = []
		for var in self.clsVar.variables:
			self.variables.append(self.modelInstance.meta.dm_variables[var.name])
	
	def connect(self, other):
		self.clsVar.checkConnect(other.clsVar)
		for (thisVar, otherVar) in zip(self.variables, other.variables):
			thisVar.connect(otherVar)


class DerivativeVector(object):
	"""
	Derivative vector in a model instance
	"""
	def __init__(self, model):
		object.__setattr__(self, 'model', model)
		object.__setattr__(self, 'dm_realStates', model.__class__.dm_realStates)
		for name in self.dm_realStates.keys():
			object.__setattr__(self, name, 0.)
	
	def __setattr__(self, name, value):
		if (name in self.dm_realStates.keys()):			
			object.__setattr__(self, name, value)
		else:
			raise FieldError('No state derivative with name {}'.format(name))
