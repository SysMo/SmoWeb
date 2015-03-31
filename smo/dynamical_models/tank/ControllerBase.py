'''
Created on Mar 4, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
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