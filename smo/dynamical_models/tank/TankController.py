'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from ControllerBase import ControllerBase
from smo.util import AttributeDict 

class TankController(ControllerBase):
	# States
	WAITING = 0
	FUELING = 1
	EXTRACTION = 2
	
	# Time events
	TE_BEGIN_FUELING = 0
	TE_BEGIN_EXTRACTION = 1
	
	class Inputs(): pass
	class Outputs(): pass
	class Parameters():
		def __init__(self, params):				
			self.tWaitBeforeExtraction = params.tWaitBeforeExtraction
			self.tWaitBeforeFueling = params.tWaitBeforeFueling
			self.pMin = params.pMin
			self.pMax = params.pMax
			self.mDotExtr = -params.mDotExtr
			self.hConvTankWaiting = params.hConvTankWaiting
			self.hConvTankExtraction = params.hConvTankExtraction
			self.hConvTankFueling = params.hConvTankFueling
			self.nCompressor = params.nCompressor
	
	def __init__(self, params = None, **kwargs):
		if params == None:
			params = AttributeDict(kwargs)
			
		self.state = params.initialState
		self.pTankInit = params.pTankInit
		self.inputs = self.Inputs()
		self.outputs = self.Outputs()
		self.parameters = self.Parameters(params)
		
		# :TRICKY: change the initial state of the controler
		if (self.pTankInit >= self.parameters.pMax and self.state == self.FUELING):
			self.state = self.EXTRACTION
			
		if (self.pTankInit <= self.parameters.pMin and self.state == self.EXTRACTION):
			self.state = self.FUELING
			
		self.executeEntryActions()
	
	def setInputs(self, **kwargs):
		self.inputs.pTank = kwargs['pTank']
	
	def checkForStateTransition(self):
		checkValue = 0
		if (self.state == self.WAITING):
			pass
		elif (self.state == self.FUELING):
			checkValue = self.inputs.pTank - self.parameters.pMax
		elif (self.state == self.EXTRACTION):
			checkValue = self.parameters.pMin - self.inputs.pTank
		return checkValue
	
	def makeStateTransition(self, solver):
		eps = 1e-10
		newState = self.state
		
		if (self.state == self.WAITING):
			pass
		elif (self.state == self.FUELING):
			if (self.inputs.pTank > (1 - eps) * self.parameters.pMax):
				if self.parameters.tWaitBeforeExtraction == 0.0:
					newState = self.EXTRACTION
				else:
					newState = self.WAITING
		elif (self.state == self.EXTRACTION):
			if (self.inputs.pTank < (1 + eps) * self.parameters.pMin):
				if self.parameters.tWaitBeforeFueling == 0.0:
					newState = self.FUELING
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
		elif (timeEvent.eventType == self.TE_BEGIN_FUELING):
			newState = self.FUELING
			
		print("State controller changing from state {} to state {} at time {} (TimeEvent)".format(self.state, newState, timeEvent.t))
		self.executeExitActions()
		self.state = newState
		self.executeEntryActions()
		
	def executeEntryActions(self):
		if (self.state == self.WAITING):
			self.outputs.nCompressor = 0.0
			self.outputs.mDotExtr = 0.0
			self.outputs.hConvTank = self.parameters.hConvTankWaiting
		elif (self.state == self.FUELING):
			self.outputs.nCompressor = self.parameters.nCompressor
			self.outputs.mDotExtr = 0.0
			self.outputs.hConvTank = self.parameters.hConvTankFueling 
		elif (self.state == self.EXTRACTION):
			self.outputs.nCompressor = 0.0 
			self.outputs.mDotExtr = self.parameters.mDotExtr
			self.outputs.hConvTank = self.parameters.hConvTankExtraction 
	
		