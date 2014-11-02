from quantity import Quantities

class Field(object):
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	
	def __init__(self, default = None, label = None):
		self.label = label
		self.default = default
		
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Field.creation_counter
		Field.creation_counter += 1

class Quantity(Field):
	def __init__(self, type, default, *args, **kwargs):
		super(Quantity, self).__init__(*args, **kwargs)
		self.type = type
		self.defaultDispUnit = default[1]
		self.default = self.setValue(default)
		
	def setValue(self, value):
		if (isinstance(value, tuple) and len(value) == 2):
			unitDef = Quantities[self.type]['units'][value[1]]
			unitOffset = 0 if ('offset' not in unitDef.keys()) else unitDef['offset']
			return value[0] * unitDef['mult'] + unitOffset
		elif (isinstance(value, (float, int))):
			return value
		else:
			raise ValueError("To set quantity value you should either use a number or a tuple e.g. (2, 'mm')")
		
class Reference(Field):
	def __init__(self, *args, **kwargs):
		super(Reference, self).__init__(*args, **kwargs)

class Group(object):
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	def __init__(self, label = None):
		self.label = label
		# Increase the creation counter, and save our local copy.
		self.creation_counter = FieldGroup.creation_counter
		FieldGroup.creation_counter += 1

class FieldGroup(Group):
	def __init__(self, fields = None, *args, **kwargs):
		super(FieldGroup, self).__init__(*args, **kwargs)
		self.fields = [] if (fields is None) else fields

class SuperGroup(Group):
	def __init__(self, groups = None, *args, **kwargs):
		super(SuperGroup, self).__init__(*args, **kwargs)
		self.groups = [] if (groups is None) else groups

		

