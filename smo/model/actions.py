class Action(object):
	pass

class ServerAction(Action):
	"""
	Server action is a command sent from the client to the server at the push of
	a button.
	"""
	def __init__(self, name, label, options = None, outputView = ''):
		self.name = name
		self.label = label
		self.outputView = outputView
		
		self.type = 'ServerAction'
		self.options = options
	def toJson(self):
		optionList = []
		if (self.options is not None):
			for optionTuple in self.options:
				optionList.append(list(optionTuple))
				
		jsonObject = {
			'name': self.name,
			'label': self.label,
			'outputView': self.outputView,
			'type': self.type,
			'options': optionList
		}
		return jsonObject

class ActionBar(object):
	"""
	`ActionBar` is a placeholder (toolbar) for buttons belonging
	to a `ModelView`. It also generates function handlers, called
	when any of the buttons is pushed.
	"""
	def __init__(self, actionList = None):
		"""
		:param list actionList: the actions assigned to this bar
		"""
		self.actionList = []
		self.actionList.append(ServerAction("compute", label = "Compute", outputView = 'resultView'))
		self.actionList.append(ServerAction("abort", label = "Abort", outputView = 'resultView'))
		self.actionList.append(ServerAction("save", label = "Save", options = (
			('local', 'Save locally'),
			('global', 'Save on server'),
		)))
		if (actionList is not None):
			self.actionList.extend(actionList)
