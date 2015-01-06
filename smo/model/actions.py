class Action(object):
	pass

class ServerAction(Action):
	def __init__(self, name, label):
		self.name = name
		self.label = label

class ActionBar(object):
	def __init__(self, actionList, save = True):
		self.actionList = actionList
		self.save = save
