from quantity import Quantities
import json
import numpy as np

class Field(object):
	"""
	Abstract base class for numerical models.
	"""
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	
	def __init__(self, label = "", show = None):
		self.label = label
		self.show = show
		if (self.show is not None):
			self.show = self.show.replace('"', '\'')
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Field.creation_counter
		Field.creation_counter += 1

class Quantity(Field):
	def __init__(self, type = 'Dimensionless', default = None, minValue = 1e-99, maxValue = 1e99, *args, **kwargs):
		super(Quantity, self).__init__(*args, **kwargs)
		self.type = type
		self.minValue = self.parseValue(minValue)
		self.maxValue = self.parseValue(maxValue)
		if (default is None):
			self.default = 1.0
			if ('defDispUnit' in Quantities[self.type].keys()):
				self.defaultDispUnit = Quantities[self.type]['defDispUnit']
			else:
				self.defaultDispUnit = Quantities[self.type]['SIUnit']
		elif (isinstance(default, tuple) and len(default) == 2):
			self.default = self.parseValue(default)
			self.defaultDispUnit = default[1]
		elif (isinstance(default, (float, int))):
			self.default = default
			if ('defDispUnit' in Quantities[self.type].keys()):
				self.defaultDispUnit = Quantities[self.type]['defDispUnit']
			else:
				self.defaultDispUnit = Quantities[self.type]['SIUnit']
		else:
			raise ValueError("To set quantity default value you should either use a number or a tuple e.g. (2, 'mm')")
		
	def parseValue(self, value):
		if (isinstance(value, tuple) and len(value) == 2):
			unitDef = Quantities[self.type]['units'][value[1]]
			unitOffset = 0 if ('offset' not in unitDef.keys()) else unitDef['offset']
			return value[0] * unitDef['mult'] + unitOffset
		elif (isinstance(value, (float, np.float32, np.float64))):
			return float(value)
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

class String(Field):
	def __init__(self, default = None, maxLength = None, multiline = None, *args, **kwargs):
		super(String, self).__init__(*args, **kwargs)
		if (default is None):
			self.default = "..."
		else:
			self.default = self.parseValue(default)
		
		if (multiline is None):
			self.multiline = False
		else:
			self.multiline = multiline
			
		if (maxLength is None):
			self.maxLength = 100
		else:
			self.maxLength = maxLength

	def parseValue(self, value):
		return value	

	def getValueRepr(self, value):
		if (self.multiline == True):
			resultStr = "";
			for i in range(len(value)/10):
				resultStr += value[:10]
				resultStr += '\n'
				value = value[10:]
			if len(value)>0:
				resultStr += value[:]
			else: resultStr=resultStr[:-1]
			return resultStr
		else:
			return value
	
	def toFormDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'String'
		fieldDict['multiline'] = self.multiline
		if (self.show is not None):
			fieldDict['show'] = self.show
		return fieldDict

class Boolean(Field):
	def __init__(self, default = None, *args, **kwargs):		
		super(Boolean, self).__init__(*args, **kwargs)
		if (default is None):
			self.default = True;
		else:
			self.default = self.parseValue(default)

	def parseValue(self, value):
		if ((value is True) or (value is False)):
			return value
		elif (value == 'true' or value == 'True'):
			return True
		elif (value == 'false' or value == 'False'):
			return False
		else:
			raise ValueError("To set boolean field you should either use boolean value or string")

	def getValueRepr(self, value):
		return value
	
	def toFormDict(self):
		fieldDict = {'name' : self._name, 'label': self.label}
		fieldDict['type'] = 'Boolean'
		if (self.show is not None):
			fieldDict['show'] = self.show
		return fieldDict

class Choices(Field):
	def __init__(self, options, default = None, maxLength = None, *args, **kwargs):
		super(Choices, self).__init__(*args, **kwargs)
		self.options = options
		if (default is None):
			self.default = options.keys()[0]
		else:
			self.default = self.parseValue(default)
			
		if (maxLength is None):
			self.maxLength = 100
		else:
			self.maxLength = maxLength
	
	def parseValue(self, value):
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
		if (self.show is not None):
			fieldDict['show'] = self.show
		return fieldDict

class ObjectReference(Field):
	def __init__(self, targetContainer, default, *args, **kwargs):
		super(ObjectReference, self).__init__(*args, **kwargs)
		self.targetContainer = targetContainer
		self.default = self.parseValue(default)
		
	def parseValue(self, value):
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

class TableView(Field):
	def __init__(self, default = None, dataLabels = None, options = None, *args, **kwargs):
		super(TableView, self).__init__(*args, **kwargs)
		if (default is None):
			self.default = np.array([])
		else:
			self.default = self.parseValue(default)
		
		if (dataLabels is None):
			self.dataLabels = []
		else:
			self.dataLabels = dataLabels		
		
		if (options is None):
			self.options = {}
		else:
			if (isinstance(options, dict)):
				self.options = options
			else:
				raise TypeError('Options passed to TableView must be a dictionary object')
	
	def parseValue(self, value):
		if (isinstance(value, np.ndarray)):
			return value
		else:
			raise TypeError('The value of TableView must be a numpy array')
		
	def toFormDict(self):
		if ('title' not in self.options.keys()):
			self.options['title'] = self.label
		
		fieldDict = {
			'name': self._name, 
			'label': self.label, 
			'type': 'TableView',
			'options': self.options
			}
		return fieldDict

	def getValueRepr(self, value):
		extendedData = value.tolist()
		extendedData.insert(0, self.dataLabels)
		return extendedData

class PlotView(Field):
	def __init__(self, default = None, dataLabels = None, xlog = None, ylog = None, options = None, *args, **kwargs):
		super(PlotView, self).__init__(*args, **kwargs)
		if (default is None):
			self.default = np.array([])
		else:
			self.default = self.parseValue(default)
		
		if (dataLabels is None):
			self.dataLabels = []
		else:
			self.dataLabels = dataLabels
			
		if (xlog is None):
			self.xlog = False
		else:
			self.xlog = xlog
			
		if (ylog is None):
			self.ylog = False
		else:
			self.ylog = ylog
		
		if (options is None):
			self.options = {}
		else:
			if (isinstance(options, dict)):
				self.options = options
			else:
				raise TypeError('Options passed to PlotView must be a dictionary object')
		
	def parseValue(self, value):
		if (isinstance(value, np.ndarray)):
			return value
		else:
			raise TypeError('The value of PlotView must be a numpy array')
	
	def getValueRepr(self, value):
		return value.tolist()

	def toFormDict(self):
		if ('title' not in self.options.keys()):
			self.options['title'] = self.label
			
		if ('width' not in self.options.keys()):
			self.options['width'] = 700
		
		if ('height' not in self.options.keys()):
			self.options['height'] = 400
		
		self.options['labels'] = self.dataLabels
		
		if ('xlabel' not in self.options.keys()):
			self.options['xlabel'] = self.dataLabels[0]
		
		if ('ylabel' not in self.options.keys()):
			self.options['ylabel'] = self.dataLabels[1]
		
		self.options['labelsDiv'] = self._name + 'LegendDiv'
		
		if ('labelsDivWidth' not in self.options.keys()):
			self.options['labelsDivWidth'] = 400
			
		self.options['labelsSeparateLines'] = True
		
		if (self.xlog):
			self.options['axes'] = { 'x' : {'logscale': True} }
		
		if (self.ylog):
			self.options['logscale'] = True
		
		fieldDict = {
			'name': self._name, 
			'label': self.label, 
			'type': 'PlotView',
			'options': self.options
			}
		return fieldDict

class Group(object):
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	def __init__(self, label = ""):
		self.label = label
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Group.creation_counter
		Group.creation_counter += 1

class FieldGroup(Group):
	def __init__(self, fields = None, *args, **kwargs):
		super(FieldGroup, self).__init__(*args, **kwargs)
		self.fields = [] if (fields is None) else fields

class ViewGroup(Group):
	def __init__(self, fields = None, *args, **kwargs):
		super(ViewGroup, self).__init__(*args, **kwargs)
		self.fields = [] if (fields is None) else fields

class SuperGroup(Group):
	def __init__(self, groups = None, *args, **kwargs):
		super(SuperGroup, self).__init__(*args, **kwargs)
		self.groups = [] if (groups is None) else groups
		
class RecordArray(Field):
	def __init__(self, structDict = None, numRows = 1, *args, **kwargs):
		super(RecordArray, self).__init__(*args, **kwargs)	
		
		if (structDict is None):
			raise ValueError('The structure of the array is not defined')
		if (len(structDict) == 0):
			raise ValueError('The structure of the array is not defined')
		
		self.fieldList = []
		typeList = []
		defaultValueList = []
		
		for name, field in structDict.items():
			structField = field
			structField._name = name
			defaultValueList.append(field.default)
			self.fieldList.append(structField)
			if isinstance(field, Quantity):
				typeList.append((field._name, np.float64))
			elif isinstance(field, Boolean): 
				typeList.append((field._name, np.dtype(bool)))
			elif (isinstance(field, String) or isinstance(field, Choices)): 
				typeList.append((field._name, np.dtype('S' + str(field.maxLength))))
			
		defaultValueList = tuple(defaultValueList)
		self.dtype = np.dtype(typeList)	
		self.default = np.zeros((numRows,), dtype = self.dtype)
		
		for i in range(numRows):
			self.default[i] = defaultValueList
		
	def parseValue(self, value):
		if (isinstance(value, np.ndarray)):
			return value
		elif (isinstance(value, list)):
			array = np.zeros((len(value),), dtype = self.dtype)
			i = 0
			for elem in value:
				if isinstance(elem, list):
					array[i] = tuple(elem)
				else:
					raise TypeError('Trying to set row of RecordArray from non-list object')
				i += 1
			return array
		else:
			raise TypeError('The value of RecordArray must be a numpy structured array or a list of lists')
	
	def getValueRepr(self, value):
		return value.tolist()

	def toFormDict(self):
		fieldDict = {'type': 'RecordArray', 
					'name': self._name,
					'label': self.label
					}
		
		jsonFieldList = []		
		for field in self.fieldList:
			jsonFieldList.append(field.toFormDict())
		
		fieldDict['fields'] = jsonFieldList
		
		return fieldDict

		
		
