'''
Created on May 10, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
class SimulationAction(object):
	"""
	Abstract base class for all simulation actions
	"""

class SetRealState(SimulationAction):
	"""
	Action, copying value from the state derivative vector to the
	model state variable
	"""
	def __init__(self, stateIndex, variableInstance):
		"""
		:param int stateIndex: global index of the state in the state vector
		:param variableInstance: variable instance
		:type variableInstance: :class:`~smo.dynamical_models.core.Fields.InstanceVariable`
		"""		
		self.stateIndex = stateIndex 
		self.variableInstance = variableInstance 
		
	def __str__(self):
		return "{.qName} = stateVector[{}]".format(
			self.variableInstance, self.stateIndex)

	def execute(self, stateVector):
		self.variableInstance.setValue(stateVector[self.stateIndex])
		
class GetRealStateDerivative(SimulationAction):
	"""
	Action, copying value from the model state variable
	derivative to the global state derivative vector
	
	"""
	def __init__(self, stateIndex, variableInstance):
		"""
		:param int stateIndex: global index of the state in the state vector
		:param variableInstance: variable instance
		:type variableInstance: :class:`~smo.dynamical_models.core.Fields.InstanceVariable`
		"""		
		self.stateIndex = stateIndex 
		self.variableInstance = variableInstance 
		
	def __str__(self):
		return "stateVectorDerivative[{}] = {.qName}Dot".format(
			self.stateIndex, self.variableInstance)
		
	def execute(self, stateDerivativeVector):
		modelInstance = self.variableInstance.modelInstance
		derValue = getattr(modelInstance.der, self.variableInstance.clsVar.name)
		stateDerivativeVector[self.stateIndex] = derValue

class CallMethod(SimulationAction):
	"""
	Calls a model computation function to compute output variables
	"""
	def __init__(self, modelInstance, methodName):
		"""
		:param modelInstance: instance of model or submodel
		:param str methodName: method name
		"""		
		self.modelInstance = modelInstance
		self.methodName = methodName
		
	def __str__(self):
		return "{.qName}.{}()".format(self.modelInstance, self.methodName)
	
	def execute(self):
		method = getattr(self.modelInstance, self.methodName)
		method()

class AssignValue(SimulationAction):
	"""
	Assigns value of a variable (or its negative) to another variable
	"""
	def __init__(self, fromVar, toVar, negate = False):
		"""
		:param fromVar: variable from which value is copied
		:type fromVar: :class:`~smo.dynamical_models.core.Fields.InstanceVariable`
		:param toVar: variable to which value is copied
		:type toVar: :class:`~smo.dynamical_models.core.Fields.InstanceVariable`
		:param bool negate: if set to ``True``, assigns the negative value of the original variable  	
		"""
		self.fromVar = fromVar
		self.toVar = toVar
		self.negate = negate
		
	def __str__(self):
		sign = "-" if (self.negate) else ""
		return "{.qName} = {}{.qName}".format(self.toVar, sign, self.fromVar)
	
	def execute(self):
		value = self.fromVar.getValue()
		if (self.negate):
			value = -value
		self.toVar.setValue(value)
