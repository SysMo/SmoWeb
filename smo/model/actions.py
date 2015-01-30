class Action(object):
	pass

class ServerAction(Action):
	"""
	Server action is a command sent from the client to the server at the push of
	a button.
	"""
	def __init__(self, name, label, outputView = ''):
		self.name = name
		self.label = label
		self.outputView = outputView
		
		self.type = 'ServerAction'
		
	def toJson(self):
		jsonObject = {
			'name': self.name,
			'label': self.label,
			'outputView': self.outputView,
			'type': self.type
		}
		return jsonObject

class ActionBar(object):
	"""
	`ActionBar` is a placeholder (toolbar) for buttons belonging
	to a `ModelView`. It also generates function handlers, called
	when any of the buttons is pushed.
	"""
	def __init__(self, actionList = None, save = True):
		"""
		:param list actionList: the actions assigned to this bar
		:param bool save: whether to display save button 
		"""
		if (actionList is None):
			self.actionList = []
		else:
			self.actionList = actionList

		if save:
			self.actionList.append(ServerAction("save", label = "Save"))
