from quantity import Quantities

class Field(object):
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	
	def __init__(self, label = None):
		self.label = label
		
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Field.creation_counter
		Field.creation_counter += 1

class Quantity(Field):
	def __init__(self, type, default = None, *args, **kwargs):
		super(Quantity, self).__init__(*args, **kwargs)
		self.type = type
		if (default is None):
			self.default = 1.0
			if ('defDispUnit' in Quantities[self.type].keys()):
				self.defaultDispUnit = Quantities[self.type]['defDispUnit']
			else:
				self.defaultDispUnit = Quantities[self.type]['SIUnit']
		elif (isinstance(default, tuple) and len(default) == 2):
			self.default = self.setValue(default)
			self.defaultDispUnit = default[1]
		elif (isinstance(default, (float, int))):
			self.default = default
			if ('defDispUnit' in Quantities[self.type].keys()):
				self.defaultDispUnit = Quantities[self.type]['defDispUnit']
			else:
				self.defaultDispUnit = Quantities[self.type]['SIUnit']
		else:
			raise ValueError("To set quantity default value you should either use a number or a tuple e.g. (2, 'mm')")
		
	def setValue(self, value):
		if (isinstance(value, tuple) and len(value) == 2):
			unitDef = Quantities[self.type]['units'][value[1]]
			unitOffset = 0 if ('offset' not in unitDef.keys()) else unitDef['offset']
			return value[0] * unitDef['mult'] + unitOffset
		elif (isinstance(value, (float, int))):
			return value
		else:
			raise ValueError("To set quantity value you should either use a number or a tuple e.g. (2, 'mm')")
	
	def getValueRepr(self, value):
		return value
		
	def toUIDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'Quantity'
		fieldDict['quantity'] = self.type
		fieldDict['defaultDispUnit'] = self.defaultDispUnit
		return fieldDict

class ObjectReference(Field):
	def __init__(self, targetContainer, default, *args, **kwargs):
		super(ObjectReference, self).__init__(*args, **kwargs)
		self.targetContainer = targetContainer
		self.default = self.setValue(default)
		
	def setValue(self, value):
		if (isinstance(value, (str, unicode))):
			try:
				return self.targetContainer[value]
			except KeyError:
				raise KeyError("The reference target container for field {0} has no object with key '{1}'".
							format(self._name, value))
		elif (isinstance(value, dict) and '_key' in value):
				return value
		else:	
			raise(TypeError('The value to set a reference must be a string (key), or dictionary (having a _key field)'))

	def getValueRepr(self, value):
		return value['_key']
		
	def toUIDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'ObjectReference'
		fieldDict['options'] = {key : value['label'] for key, value in self.targetContainer.iteritems()}
		return fieldDict
	

class Group(object):
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	def __init__(self, label = None):
		self.label = label
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Group.creation_counter
		Group.creation_counter += 1

class FieldGroup(Group):
	def __init__(self, fields = None, *args, **kwargs):
		super(FieldGroup, self).__init__(*args, **kwargs)
		self.fields = [] if (fields is None) else fields

class SuperGroup(Group):
	def __init__(self, groups = None, *args, **kwargs):
		super(SuperGroup, self).__init__(*args, **kwargs)
		self.groups = [] if (groups is None) else groups

		

