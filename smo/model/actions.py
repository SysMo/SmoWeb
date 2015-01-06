class Action(object):
	pass

class ServerAction(Action):
	def __init__(self, name, label, outputView):
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
	def __init__(self, actionList, save = True):
		self.actionList = actionList
		self.save = save
