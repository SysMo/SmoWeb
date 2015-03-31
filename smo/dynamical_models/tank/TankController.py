'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from billiard.managers import State

class ControllerBase(object):
	def checkForStateTransition(self, *kwargs):
		raise NotImplementedError("The subclasses of ControllerBase need to implement 'checkForStateTransition' method")
	
	def executeEntryActions(self):
		pass
	
	def executeExitActions(self):
		pass
	
	def getStateFlag(self):
		newState = self.checkForStateTransition()
		if (newState is None):
			return -1.0
		else:
			return 1.0 

class TankController(ControllerBase):
	# States
	WAITING = 0
	REFUELING = 1
	EXTRACTION = 2
	
	# Time events
	BEGIN_REFUELING = 0
	END_REFUELING = 1
	BEGIN_EXTRACTION = 2
	END_EXTRACTION = 3
	class Inputs(): pass
	class Outputs(): pass
	class Parameters():
		def __init__(self, **kwargs):
			self.pMin = kwargs.get('pMin', 20e5)
			self.pMax = kwargs.get('pMax', 300e5)
	
	def __init__(self, initialState, **kwargs):
		self.state = initialState
		self.inputs = self.Inputs()
		self.outputs = self.Outputs()
		self.parameters = self.Parameters(**kwargs)
		
		
		self.executeEntryActions()
		self.eps = 0.0
	
	def setInputs(self, **kwargs):
		self.inputs.pTank =  kwargs['pTank']
	
	def checkForStateTransition(self):
		checkValue = 0
		if (self.state == self.WAITING):
			pass
		elif (self.state == self.REFUELING):
			checkValue = self.inputs.pTank - self.parameters.pMax
		elif (self.state == self.EXTRACTION):
			checkValue = self.parameters.pMin - self.inputs.pTank
		return checkValue
	
	def makeStateTransition(self, solver):
		self.eps = 1e-10
		newState = self.state
		
		if (self.state == self.WAITING):
			pass
		elif (self.state == self.REFUELING):
			if (self.inputs.pTank > (1 - self.eps) * self.parameters.pMax):
				newState = self.EXTRACTION
		elif (self.state == self.EXTRACTION):
			if (self.inputs.pTank < (1 + self.eps) * self.parameters.pMin):
				newState = self.REFUELING
		
		self.eps = 0.0
		print("State controller changing from state {} to state {} at time {}".format(self.state, newState, solver.t))
		self.executeExitActions()
		self.state = newState
		self.executeEntryActions()
		
	def processTimeEvent(self, timeEvent):
		newState = self.state
		if (timeEvent.eventType == self.END_REFUELING or timeEvent.eventType == self.BEGIN_EXTRACTION):
			newState = self.EXTRACTION
		elif (timeEvent.eventType == self.END_EXTRACTION or timeEvent.eventType == self.BEGIN_REFUELING):
			newState = self.REFUELING
		print("State controller changing from state {} to state {} at time {}".format(self.state, newState, timeEvent.t))
		self.executeExitActions()
		self.state = newState
		self.executeEntryActions()
		
	def executeEntryActions(self):
		if (self.state == self.WAITING):
			self.outputs.nPump = 0.0
			self.outputs.hConvTank = 10.0
		elif (self.state == self.REFUELING):
			self.outputs.nPump = 0.53 * 1.44
			self.outputs.hConvTank = 100.0
		elif (self.state == self.EXTRACTION):
			self.outputs.nPump = 0.0
			self.outputs.hConvTank = 15.0
	
		