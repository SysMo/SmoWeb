'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from ControllerBase import ControllerBase

class TankController(ControllerBase):
	# States
	WAITING = 0
	REFUELING = 1
	EXTRACTION = 2
	
	# Time events
	TE_BEGIN_REFUELING = 0
	TE_BEGIN_EXTRACTION = 1
	
	class Inputs(): pass
	class Outputs(): pass
	class Parameters():
		def __init__(self, **kwargs):
			self.pMin = kwargs.get('pMin', 20e5) #:TODO: Param
			self.pMax = kwargs.get('pMax', 300e5)
			self.tWaitBeforeExtraction = kwargs.get('tWaitBeforeExtraction', 50.)
			self.tWaitBeforeRefueling = kwargs.get('tWaitBeforeRefueling', 50.)
			self.mDotExtr = kwargs.get('mDotExtr', -30./3600)
	
	def __init__(self, initialState, **kwargs):
		self.state = initialState
		self.inputs = self.Inputs()
		self.outputs = self.Outputs()
		self.parameters = self.Parameters(**kwargs)
		
		self.executeEntryActions()
	
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
		eps = 1e-10
		newState = self.state
		
		if (self.state == self.WAITING):
			pass
		elif (self.state == self.REFUELING):
			if (self.inputs.pTank > (1 - eps) * self.parameters.pMax):
				if self.parameters.tWaitBeforeExtraction == 0.0:
					newState = self.EXTRACTION
				else:
					newState = self.WAITING
		elif (self.state == self.EXTRACTION):
			if (self.inputs.pTank < (1 + eps) * self.parameters.pMin):
				if self.parameters.tWaitBeforeRefueling == 0.0:
					newState = self.REFUELING
				else:
					newState = self.WAITING
				
		print("State controller changing from state {} to state {} at time {} (StateEvent)".format(self.state, newState, solver.t))
		self.executeExitActions()
		self.state = newState
		self.executeEntryActions()
		
	def processTimeEvent(self, timeEvent):
		newState = self.state
		if (timeEvent.eventType == self.TE_BEGIN_EXTRACTION):
			newState = self.EXTRACTION
		elif (timeEvent.eventType == self.TE_BEGIN_REFUELING):
			newState = self.REFUELING
			
		print("State controller changing from state {} to state {} at time {} (TimeEvent)".format(self.state, newState, timeEvent.t))
		self.executeExitActions()
		self.state = newState
		self.executeEntryActions()
		
	def executeEntryActions(self):
		if (self.state == self.WAITING):
			self.outputs.nPump = 0.0 
			self.outputs.mDotExtr = 0.0
			self.outputs.hConvTank = 10.0 #:TODO: Param
		elif (self.state == self.REFUELING):
			self.outputs.nPump = 0.53 * 1.44 
			self.outputs.mDotExtr = 0.0
			self.outputs.hConvTank = 100.0 
		elif (self.state == self.EXTRACTION):
			self.outputs.nPump = 0.0 
			self.outputs.mDotExtr = self.parameters.mDotExtr
			self.outputs.hConvTank = 15.0 
	
		