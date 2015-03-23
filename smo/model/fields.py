from quantity import Quantities
import os
import numpy as np
from smo.web.exceptions import *
from assimulo.support import OrderedDict

class Field(object):
	"""
	Abstract base class for all the field types.
	"""
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	
	def __init__(self, label = "", description = "", show = None):
		"""
	 	:param str label: the text label used in the user interface usually in front of the field
	 	:param str description: description to show as tooltip when hovering over the field label
		:param str show: expression (as a string), which is evaluated on the client side and is used to 
			dynamically show and hide a field, based on the values of other fields. The
			other fields in the model are referenced by prefixing them with ``self.``
		"""
		self.label = label
		self.description = description
		self.show = show
		if (self.show is not None):
			self.show = self.show.replace('"', '\'')
			
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Field.creation_counter
		Field.creation_counter += 1
	
	def parseValue(self, value):
		"""
		:param value: value to parse
		
		Checks if the ``value`` is of valid type for this field type, and, if not, 
		attempts to convert it into one.
   		For example if the Field is of type :class:`Quantity`\ ('Length') 
   		then parseValue((2, 'mm')) will return 2e-3 (in the base SI unit 'm') which
   		can be assigned to the field. Used implicitly by the 
   		:func:`smo.model.model.NumericalModel.__setattr__` method
   		"""
		raise NotImplementedError
	
	def getValueRepr(self, value):
		"""
		Converts the value of the field to a form suitable for JSON serialization
		"""
		raise NotImplementedError
	
	def toFormDict(self):
		"""
		Converts the definition of the field to a form suitable for JSON serialization
		"""
		fieldDict = {'name' : self._name, 'label': self.label}
		if (self.show is not None):
			fieldDict['show'] = self.show
		fieldDict['description'] = self.description		
		return fieldDict

class Quantity(Field):
	'''
	Represents a physical quantity (e.g. Length, Time, Mass etc.). Allows values to 
	be set using units e.g. (2, 'km')  
	'''
	def __init__(self, type = 'Dimensionless', default = None, minValue = 1e-99, maxValue = 1e99, *args, **kwargs):
		"""
		:param str type: the quantity type (Length, Mass, Time etc.)
		:param default: default value for the field. Could be a number or a tuple (value, unit)
			like (2, 'mm')
		:param float minValue: the minimum allowed value for the field
		:param float maxValue: the maximum allowed value for the field
		"""
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
		fieldDict = super(Quantity, self).toFormDict()			
		fieldDict['type'] = 'Quantity'
		fieldDict['quantity'] = self.type
		fieldDict['defaultDispUnit'] = self.defaultDispUnit
		fieldDict['minValue'] = self.minValue
		fieldDict['maxValue'] = self.maxValue
		unitsList = []
		for key in Quantities[self.type]['units'].keys():			
			unitsList.append([key, Quantities[self.type]['units'][key]])
		fieldDict['units'] = unitsList
		fieldDict['title'] = Quantities[self.type]['title']
		fieldDict['nominalValue'] = Quantities[self.type]['nominalValue']
		fieldDict['SIUnit'] = Quantities[self.type]['SIUnit']
		return fieldDict

class String(Field):
	"""
	Represents a string field
	"""
	def __init__(self, default = None, maxLength = None, multiline = None, *args, **kwargs):
		"""
		:param str default: default value
		:param int maxLength: the maximum number of characters in the string
		:param bool multiline: whether line breaks are allowed in the string
		"""
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
		fieldDict = super(String, self).toFormDict()
		fieldDict['type'] = 'String'
		fieldDict['multiline'] = self.multiline
		return fieldDict

class Boolean(Field):
	"""
	Represents a boolean value (True or False)
	"""
	def __init__(self, default = None, *args, **kwargs):
		""":param bool default: default value"""
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
		fieldDict = super(Boolean, self).toFormDict()
		fieldDict['type'] = 'Boolean'		
		return fieldDict

class Choices(Field):
	"""
	Allows the user to make a choice from a list of options
	"""
	def __init__(self, options, default = None, maxLength = None, *args, **kwargs):
		"""
		:param options: dictionary or ordered dictionary containing the possible 
			choices represented by (value, label) pairs. The label is used in the
			display combo-box
		:param default: default value (from options)
		:param maxLength: ???
		"""
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
		fieldDict = super(Choices, self).toFormDict()
		fieldDict['type'] = 'Choices'
		optionsList = []
		for key in self.options.keys():			
			optionsList.append([key, self.options[key]])
		fieldDict['options'] = optionsList
		return fieldDict

class ObjectReference(Field):
	"""
	Object reference
	"""
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
			raise(ArgumentTypeError('The value to set a reference must be a string (key), or dictionary (having a _key field)'))

	def getValueRepr(self, value):
		return value['_key']
		
	def toFormDict(self):
		fieldDict = super(ObjectReference, self).toFormDict()
		fieldDict['type'] = 'Choices'
		optionsList = []
		for key in self.targetContainer.keys():			
			optionsList.append([key, self.targetContainer[key]['label']])
		fieldDict['options'] = optionsList
# 		fieldDict['options'] = {key : value['label'] for key, value in self.targetContainer.iteritems()}
		return fieldDict

class RecordArray(Field):
	"""
	Composite input field for representing a structured table (array of records)
	"""
	def __init__(self, structTuple = None, numRows = 1, *args, **kwargs):
		"""
		:param structTuple: tuple defining the structure of the 
			record array. It consists of ``(name, type)`` pairs, 
			where ``name`` is the column name, and ``type`` is one of the basic
			field types (:class:`Quantity`, :class:`String`, :class:`Boolean` etc.)
		:param int numRows: the initial number of rows in the table
		
		Example::
		
			compositePipe = RecordArray(
				(
					('name', String(maxLength = 20)),
					('length', Quantity('Length')),
					('diameter', Quantity('Length')),	   
				), label='composite pipe'
			)
  
		"""
		super(RecordArray, self).__init__(*args, **kwargs)	
		
		if (structTuple is None):
			raise ValueError('The structure of the array is not defined')
		if (len(structTuple) == 0):
			raise ValueError('The structure of the array is not defined')
		
		structDict = OrderedDict(structTuple)
		
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
					raise ArgumentTypeError('Trying to set row of RecordArray from non-list object')
				i += 1
			return array
		else:
			raise ArgumentTypeError('The value of RecordArray must be a numpy structured array or a list of lists')
	
	def getValueRepr(self, value):
		return value.tolist()

	def toFormDict(self):
		fieldDict = super(RecordArray, self).toFormDict()
		fieldDict['type'] = 'RecordArray'
		jsonFieldList = []		
		for field in self.fieldList:
			jsonFieldList.append(field.toFormDict())
		fieldDict['fields'] = jsonFieldList
		return fieldDict
	
class DataSeriesView(Field):
	"""
	Composite output field for representing a table or plot
	"""
	def __init__(self, structTuple = None, visibleColumns = None, *args, **kwargs):
		"""
		:param structTuple: tuple defining the structure of the 
			view data. It consists of ``(name, type)`` pairs, 
			where ``name`` is the column name, and ``type`` is one of the basic
			field types (:class:`Quantity`, :class:`String`, :class:`Boolean` etc.)
		
		Example::
				(
					('pressure', Quantity('Pressure')),
					('temperature', Quantity('Temperature')),	   
				)
		:param visibleColumns: list of integers specifying which columns of the view data are visible
		"""
		super(DataSeriesView, self).__init__(*args, **kwargs)	
		
		if (structTuple is None):
			raise ValueError('The data structure is not defined.')
		if (len(structTuple) == 0):
			raise ValueError('The data structure is not defined.')
		
		structDict = OrderedDict(structTuple)
		
		self.fieldList = []
		typeList = []
		defaultValueList = []
		self.dataLabels = []
		
		for name, field in structDict.items():
			structField = field
			structField._name = name
			self.dataLabels.append(name)
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
		self.default = np.zeros((1,), dtype = self.dtype)
		
		for i in range(1):
			self.default[i] = defaultValueList
			
		if (visibleColumns is None):
			self.visibleColumns = [n for n in range(len(self.dataLabels))]
		else:
			self.visibleColumns = visibleColumns
		
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
					raise ArgumentTypeError('Trying to set row of View from non-list object')
				i += 1
			return array
		else:
			raise ArgumentTypeError('The value of View must be a numpy structured array or a list of lists')
	
	def getValueRepr(self, value):
		return value.tolist()

	def toFormDict(self):
		fieldDict = super(DataSeriesView, self).toFormDict()
		fieldDict['type'] = 'View'
		jsonFieldList = []		
		for field in self.fieldList:
			jsonFieldList.append(field.toFormDict())
		fieldDict['fields'] = jsonFieldList
		fieldDict['labels'] = self.dataLabels
		fieldDict['visibleColumns'] = self.visibleColumns
		return fieldDict

class TableView(DataSeriesView):
	"""
	Field for visualization of table data
	"""
	def __init__(self, structTuple = None, options = None, *args, **kwargs):
		"""
		:param structTuple: tuple defining the structure of the view data. \
		It consists of ``(name, type)`` pairs, \
		where ``name`` is the column name, and ``type`` is the :class:`Quantity` field type
		
		Example::
				(	('pressure', Quantity('Pressure')),
					('temperature', Quantity('Temperature'))	)
				
		:param dict options: additional options to be passed
		
		"""
		
		if (options is None):
			self.options = {}
		else:
			if (isinstance(options, dict)):
				self.options = options
			else:
				raise ArgumentTypeError('Options passed to TableView must be a dictionary object')
		
		super(TableView, self).__init__(structTuple = structTuple, *args, **kwargs)
		
	def toFormDict(self):
		fieldDict = super(TableView, self).toFormDict()
		if ('title' not in self.options.keys()):
			self.options['title'] = self.label
		
		fieldDict['options'] = self.options
		fieldDict['type'] = 'TableView'
		return fieldDict

class PlotView(DataSeriesView):
	"""
	Field for creating interactive plots
	"""
	def __init__(self, structTuple = None, xlog = None, ylog = None, options = None, *args, **kwargs):
		"""
		:param structTuple: tuple defining the structure of the view data. \
		It consists of ``(name, type)`` pairs, \
		where ``name`` is the column name, and ``type`` is the :class:`Quantity` field type
		
		Example::
				(	('pressure', Quantity('Pressure')),
					('temperature', Quantity('Temperature'))	)
				
		:param bool xlog: use logarithmic scale for x axis
		:param bool ylog: use logarithmic scale for y axis
		:param dict options: additional options to be passed
		
		"""
		
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
				raise ArgumentTypeError('Options passed to TableView must be a dictionary object')
		
		super(PlotView, self).__init__(structTuple = structTuple, *args, **kwargs)
		
	def toFormDict(self):
		fieldDict = super(PlotView, self).toFormDict()
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
			self.options['ylabel'] = None
		
		if ('labelsDivWidth' not in self.options.keys()):
			self.options['labelsDivWidth'] = 400
			
		self.options['labelsSeparateLines'] = True
		
		if (self.xlog):
			self.options['axes'] = { 'x' : {'logscale': True} }
		
		if (self.ylog):
			self.options['logscale'] = True
		
		fieldDict['options'] = self.options
		fieldDict['type'] = 'PlotView'
		return fieldDict

# class VariationTable(TableView):
# 	def __init__(self, default = None, dataLabels = None, quantities = None, 
# 				visibleColumns = None, options = None, parentCollection = None, fieldName = None, *args, **kwargs):
# 		if (fieldName is None):
# 			raise ValueError('VariationTable constructor must be passed the name of the Variation Table field.')
# 		if (parentCollection is None):
# 			raise ValueError('VariationTable constructor must be passed a parent MongoDB collection.')
# 		else:
# 			self.collection = parentCollection[fieldName]	
# 			
# 		if (default is None):
# 			default = VariationTableValue(recordId = '', newRow = [], collection = self.collection, varTableName = fieldName)
# 		else:
# 			default = self.parseValue(default)
# 			
# 		super(VariationTable, self).__init__(default, dataLabels, quantities, 
# 									visibleColumns, options, *args, **kwargs)
# 		
# 	def parseValue(self, valueObj):
# 		if (isinstance(valueObj, VariationTableValue)):
# 			return valueObj
# 		else:
# 			raise ArgumentTypeError('The value of VariationTable must be a VariationTableValue object')
# 		
# 	def getValueRepr(self, valueObj):
# 		extendedData = valueObj.value.tolist()
# 		extendedData.insert(0, self.dataLabels)
# 		return extendedData

class Image(Field):
	"""
	Field for displaying an image 
	"""
	def __init__(self, default = None, width = None, height = None, *args, **kwargs):
		"""
		:param str src: path to image source
		:param int width: image width
		:param int height: image height
		"""
		super(Image, self).__init__(*args, **kwargs)
		if default is None:
			raise ArgumentError("Image field constructor must be passed string argument 'default' specifying image source path.")
		else:
			self.default = default
		
		if width is None:
			self.width = 700
		else:
			self.width = width
			
		if height is None:
			self.height = 400
		else:
			self.height = height
	
	def parseValue(self, value):
		return value

	def getValueRepr(self, value):
		return value
	
	def toFormDict(self):
		fieldDict = super(Image, self).toFormDict()
		fieldDict['type'] = 'Image'
		fieldDict['width'] = self.width	
		fieldDict['height'] = self.height			
		return fieldDict

class SubModelGroup(Field):
	"""
	Include field group or supergroup from a sub-model
	"""
	def __init__(self, klass, group, *args, **kwargs):
		Field.__init__(self, *args, **kwargs)
		self.group = group
		self.klass = klass
		self.show = kwargs.get('show', True)
			
class Group(object):
	"""Abstract class for group of fields"""
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	def __init__(self, label = "", show = True):
		self.label = label
		self.show = show
		# Increase the creation counter, and save our local copy.
		self.creation_counter = Group.creation_counter
		Group.creation_counter += 1

class BasicGroup(Group):
	def __init__(self, fields = None, *args, **kwargs):
		super(BasicGroup, self).__init__(*args, **kwargs)
		self.fields = []
		self.unresolved_fields = []
		if (fields is not None):
			for field in fields:
				if isinstance(field, str):
					self.unresolved_fields.append(field)
				else:
					self.fields.append(field)

class FieldGroup(BasicGroup):
	"""Represents a group of fields of all basic types except for PlotView and TableView"""
	pass

class ViewGroup(BasicGroup):
	"""Represents a group of fields of type PlotView and/or TableView"""
	pass

class SuperGroup(Group):
	"""Represents a group of FieldGroup and/or ViewGroup groups"""
	def __init__(self, groups = None, *args, **kwargs):
		super(SuperGroup, self).__init__(*args, **kwargs)
		self.groups = [] if (groups is None) else groups
		
	def update(self, groups):
		for group in groups:
			if (group not in self.groups):
				self.groups.append(group)

class ModelView(object):
	"""
	Represents a view of the numerical model, comprised of super-groups and a bar of buttons for performing actions.
	
	:param str ioType: the type of the view. It may be *input*, 
		requiring the user to enter input data, or *output*, displaying the results of the computation
	:param list superGroups: a list of ``SuperGroup`` objects
	:param ActionBar actionBar: an ``ActionBar`` object	
	:param bool autoFetch: used to specify whether the view should be loaded automatically at the client
	"""
	def __init__(self, ioType, superGroups, actionBar = None, autoFetch = False):
		self.ioType = ioType
		self.superGroups = superGroups
		self.actionBar = actionBar
		self.autoFetch = autoFetch
		
class ModelFigure(object):
	""" Represents a figure displayed with the numerical model """
	def __init__(self, src = None, width = None, height = None, show = True):
		if (src == None):
			raise ValueError('File path missing as first argument.')
		else:
			self.src = src
		srcFolder, fileName = os.path.split(self.src)
		baseName, ext = os.path.splitext(fileName)
		self.thumbSrc = os.path.join(srcFolder, 'thumbnails', baseName + '_thumb.png')
		if (width == None):
			self.width = 'auto'
		else:
			self.width= width
		if (height == None):
			self.height = 'auto'
		else:
			self.height= height
		
		self.show = show
			
class ModelDescription(object):
	""" Description of the numerical model """
	def __init__(self, text, asTooltip = None, show = False):
		self.text = text
		self.show = show
		if (asTooltip is None):
			self.asTooltip = text
		else:
			self.asTooltip = asTooltip