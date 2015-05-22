'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
import StringIO
import SimulationActions as SA
import Fields as F

class DynamicalModelMeta(type):
	"""
	Meta-model for creating dynamical model classes 
	"""
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		
		# Collect fields from current class.
		dm_variables = []
		dm_submodels = []
		dm_realStates = []
		dm_functions = []
		dm_ports = []
		for key, value in attrs.items():
			if isinstance(value, F.ScalarVariable):
				dm_variables.append((key, value))
				value.setName(key)
				attrs.pop(key)
				if (isinstance(value, F.RealState)):
					dm_realStates.append((key, value))
			elif isinstance(value, F.Function):
				dm_functions.append((key, value))
				value.setName(key)
				attrs[key] = value.funcDef
			elif isinstance(value, F.Port):
				dm_ports.append((key, value))
				value.setName(key)
				attrs.pop(key)
			elif isinstance(value, F.SubModel):
				dm_submodels.append((key, value))
				value.setName(key)
				attrs.pop(key)
		
		# Create special class variables with the collected fields
		dm_variables.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_variables'] = OrderedDict(dm_variables)
		dm_realStates.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_realStates'] = OrderedDict(dm_realStates)
		dm_functions.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_functions'] = OrderedDict(dm_functions)
		dm_ports.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_ports'] = OrderedDict(dm_ports)
		dm_submodels.sort(key=lambda x: x[1].creation_counter)
		attrs['dm_submodels'] = OrderedDict(dm_submodels)
		
		new_class = (super(DynamicalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		return new_class

		
class InstanceMeta(object):
	"""
	InstanceMeta links instance attributes (variables , functions, ports) to
	class definitions (fields declared in a DynamicalModel subclass). It has
	the following attributes:
	
		* :attr:`dm_variables` 
		* :attr:`dm_submodels` 
		* :attr:`dm_functions` 
		* :attr:`dm_ports` 
	 
	"""
	def __init__(self):
		self.dm_variables = {}
		self.dm_submodels = {}
		self.dm_functions = {}
		self.dm_ports = {}
		
	def addInstanceVariable(self, instanceVariable):
		varName = instanceVariable.clsVar.name
		self.dm_variables[varName] = instanceVariable
		self.__setattr__(varName, instanceVariable)
		
	def addInstanceFunction(self, instanceFunction):
		funcName = instanceFunction.clsVar.name
		self.dm_functions[funcName] = instanceFunction
		self.__setattr__(funcName, instanceFunction)
		
	def addInstancePort(self, instancePort):
		portName = instancePort.clsVar.name
		self.dm_ports[portName] = instancePort
		self.__setattr__(portName, instancePort)

class DynamicalModel(object):
	"""
	Base class for all dynamical models
	Attributes:
	
		* :attr:`meta` : an instance of :class:`InstanceMeta`, used to access
		  field definitions
		* :attr:`der` : instance of :class:`DerivativeVector`, used to work with
		  the model derivatives
		* :attr:`qPath` : qualified pathof this model instance in the hierarcy
		  of the root model
		* :attr:`sim` : the simulation compiler assigned to the top-leve model
		  
	
	"""
	__metaclass__ = DynamicalModelMeta
	
	def __new__(cls, name = None, parent = None, *args, **kwargs):
		"""
		Constructor for all dynamical models. Sets default values for all model fields

		:param name: name of the instance
		:param parent : if this is submodel in another model, this is the 
			parent model instance
		"""
		self = object.__new__(cls)
		if (name is None):
			name = cls.__name__
		self.name = name
		self.parent = parent
		if (self.parent is not None):
			self.qPath = self.parent.qPath + [self.name]
		else:
			from SimulationCompiler import SimulationCompiler
			self.qPath = [self.name]
			self.simCmpl = SimulationCompiler(self)
		# Create instance meta
		self.meta = InstanceMeta()
		# Create derivative vector
		self.der = F.DerivativeVector(self)
		# Create instance variables
		for name, clsVar in cls.dm_variables.iteritems():
			self.meta.addInstanceVariable(F.InstanceVariable(
					modelInstance = self, clsVar = clsVar))
			setattr(self, clsVar.name, clsVar.default)
		# Create instance functions
		for name, clsVar in cls.dm_functions.iteritems():
			self.meta.addInstanceFunction(F.InstanceFunction(
					modelInstance = self, clsVar = clsVar))
		# Create instance ports
		for name, clsVar in cls.dm_ports.iteritems():
			self.meta.addInstancePort(F.InstancePort(
					modelInstance = self, clsVar = clsVar))
		# Create submodel instances
		for name, submodel in cls.dm_submodels.iteritems():
			instance = submodel.klass(name, self)
			self.__dict__[name] = instance
			self.meta.dm_submodels[name] = instance
			
		return self
	
	@property
	def qName(self):
		""""""
		return '.'.join(self.qPath)
	
	def compute(self):
		#print("Executing compute for {}".format(self.qName))
		pass
			
	def computeDerivatives(self, stateVector, stateDerivatives):
		"""
		Execute the simulation sequence to compute derivatives
		"""		
		for action in self.simCmpl.actionSequence:
			if isinstance(action , SA.SetRealState):
				action.execute(stateVector)
			elif isinstance(action, SA.GetRealStateDerivative):
				action.execute(stateDerivatives)
			else:
				action.execute()

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
	
			