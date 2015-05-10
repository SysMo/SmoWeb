'''
Created on May 10, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
class SimulationAction(object):
	pass

class SetRealState(SimulationAction):
	def __init__(self, stateIndex, variableInstance):
		self.stateIndex = stateIndex 
		self.variableInstance = variableInstance 
		
	def __str__(self):
		return "{.qName} = stateVector[{}]".format(
			self.variableInstance, self.stateIndex)

class GetRealStateDerivative(SimulationAction):
	def __init__(self, stateIndex, variableInstance):
		self.stateIndex = stateIndex 
		self.variableInstance = variableInstance 
		
	def __str__(self):
		return "stateVectorDerivative[{}] = {.qName}Dot".format(
			self.stateIndex, self.variableInstance)

class CallMethod(SimulationAction):
	def __init__(self, modelInstance, methodName):
		self.modelInstance = modelInstance
		self.methodName = methodName
		
	def __str__(self):
		return "{.qName}.{}()".format(self.modelInstance, self.methodName)

class AssignValue(SimulationAction):
	def __init__(self, sourceVariable, destVariable):
		self.sourceVariable = sourceVariable
		self.destVariable = destVariable
		
	def __str__(self):
		return "{.qName} = {.qName}".format(self.destVariable, self.sourceVariable)