from quantity import Quantities
import json

class Field(object):
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	
	def __init__(self, label = None, show = None):
		self.label = label
		self.show = show
		
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Field.creation_counter
		Field.creation_counter += 1

class Quantity(Field):
	def __init__(self, type, default = None, minValue = 1e-99, maxValue = 1e99, *args, **kwargs):
		super(Quantity, self).__init__(*args, **kwargs)
		self.type = type
		self.minValue = self.setValue(minValue)
		self.maxValue = self.setValue(maxValue)
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
		elif (isinstance(value, float)):
			return value
		elif (isinstance(value, int)):
			return float(value)
		else:
			raise ValueError("To set quantity value you should either use a number or a tuple e.g. (2, 'mm')")
	
	def getValueRepr(self, value):
		return value
		
	def toFormDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'Quantity'
		fieldDict['quantity'] = self.type
		fieldDict['defaultDispUnit'] = self.defaultDispUnit
		fieldDict['minValue'] = self.minValue
		fieldDict['maxValue'] = self.maxValue
		if (self.show is not None):
			fieldDict['show'] = self.show
		unitsList = []
		for key in Quantities[self.type]['units'].keys():			
			unitsList.append([key, Quantities[self.type]['units'][key]])
		fieldDict['units'] = unitsList
		fieldDict['title'] = Quantities[self.type]['title']
		fieldDict['nominalValue'] = Quantities[self.type]['nominalValue']
		fieldDict['SIUnit'] = Quantities[self.type]['SIUnit']
		return fieldDict

class Choices(Field):
	def __init__(self, options, default = None, *args, **kwargs):
		super(Choices, self).__init__(*args, **kwargs)
		self.options = options
		if (default is None):
			self.default = options.keys()[0]
		else:
			self.default = self.setValue(default)
	
	def setValue(self, value):
		if (value in self.options.keys()):
			return value
		else:
			raise ValueError('Illegal value {0} for choices variable!'.format(value))		
	
	def getValueRepr(self, value):
		return value
	
	def toFormDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'Choices'
		optionsList = []
		for key in self.options.keys():			
			optionsList.append([key, self.options[key]])
		fieldDict['options'] = optionsList
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
		
	def toFormDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'Choices'
		optionsList = []
		for key in self.targetContainer.keys():			
			optionsList.append([key, self.targetContainer[key]['label']])
		fieldDict['options'] = optionsList
# 		fieldDict['options'] = {key : value['label'] for key, value in self.targetContainer.iteritems()}
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

		

