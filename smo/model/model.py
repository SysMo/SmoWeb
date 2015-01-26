import fields
from collections import OrderedDict
import copy
from smo.model.fields import FieldGroup, ViewGroup

class ModelView(object):
	def __init__(self, ioType, superGroups, actionBar = None, autoFetch = False):
		self.ioType = ioType
		self.superGroups = superGroups
		self.actionBar = actionBar
		self.autoFetch = autoFetch

class ModelFigure(object):
	def __init__(self, src = None, width = None, height = None):
		if (src == None):
			raise ValueError('File path missing as first argument.')
		else:
			self.src = src
		if (width == None):
			self.width = 'auto'
		else:
			self.width= width
		if (height == None):
			self.height = 'auto'
		else:
			self.height= height
			
class ModelDescription(object):
	def __init__(self, text, show=False):
		self.text = text
		self.show = show

class CodeBlock(object):
	def __init__(self, srcType = None, src = None):
		if (srcType == None):
			self.srcType = 'string'
			if (src == None):
				self.src = ''
			else:
				self.src = src
		elif (srcType == 'file'):
			self.srcType = srcType
			if (src == None):
				raise ValueError('File path missing as second argument.')
			else:
				self.src = src
		elif (srcType == 'string'):
			self.srcType = srcType
			if (src == None):
				self.src = ''
			else:
				self.src = src
		else:
			raise ValueError("Valid source types are 'string' and 'file'.")
			
class HtmlBlock(CodeBlock):
	pass

class JsBlock(CodeBlock):
	pass

#TODO: Currently inheritance not supported
class NumericalModelMeta(type):
	"""Metaclass facilitating the creation of a numerical
	model class. Collects all the declared fields in a 
	dictionary ``self.declared_fields``"""
	def __new__(cls, name, bases, attrs):
		# Name and label
		if ('name' not in attrs):
			attrs['name'] = name 
		if ('label' not in attrs):
			attrs['label'] = attrs['name']
		if ('title' not in attrs):
			attrs['title'] = attrs['label']
		# Collect fields from current class.
		current_fields = []
# 		current_groups = []
		for key, value in list(attrs.items()):
			if isinstance(value, fields.Field):
				current_fields.append((key, value))
				value._name = key
				attrs.pop(key)
			elif isinstance(value, fields.Group):
				value._name = key
			elif isinstance(value, ModelView):
				value.name = key
			elif isinstance(value, HtmlBlock):
				value.name = key
				
		current_fields.sort(key=lambda x: x[1].creation_counter)
		attrs['declared_fields'] = OrderedDict(current_fields)
# 		current_groups.sort(key=lambda x: x[1].creation_counter)
# 		attrs['declared_groups'] = OrderedDict(current_groups)

		new_class = (super(NumericalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		# Collect fields from base classes
		base_fields = OrderedDict()
		for c in reversed(new_class.__mro__[1:]):			
			if hasattr(c, 'declared_fields'):
				# Checks for already declared fields in base classes
				for key in c.declared_fields:
					if key in new_class.declared_fields:
						raise AttributeError("Base class {0} already has field '{1}'.".format(c.__name__, key))
				base_fields.update(c.declared_fields)		
				
		new_class.declared_fields.update(base_fields)
		
		# Resolving unresolved fields in field- and view-groups
		for key, value in new_class.__dict__.iteritems():
			if isinstance(value, FieldGroup) or isinstance(value, ViewGroup):
				for i in range(len(value.unresolved_fields)):
					unresolved_field = value.unresolved_fields.pop(i)
					value.fields.append(new_class.declared_fields[unresolved_field])	
		
		return new_class

class NumericalModel(object):
	"""Abstract base class for numerical models."""

	__metaclass__ = NumericalModelMeta
	
	def __new__(cls, *args, **kwargs):
		"""Constructor for all numerical models. 
		Sets default values for all model fields"""
		self = object.__new__(cls)
		for name, field in self.declared_fields.iteritems():
			if (isinstance(object, fields.RecordArray)):
				self.__setattr__(name, field.default.copy())
			else:
				self.__setattr__(name, field.default)  
		for name, value in kwargs.iteritems():
			self.__setattr__(name, value)
		return self
	
	def __setattr__(self, name, value):
		"""Sets field value using the :func:`Field.parseValue` method"""
		if name in self.declared_fields.keys():
			object.__setattr__(self, name, self.declared_fields[name].parseValue(value))
		else:
			raise AttributeError("Class '{0}' has no field '{1}'".format(self.__class__.__name__, name))
	
	def __getattr__(self, name):
		return object.__getattribute__(self, name)
	
	def modelView2Json(self, modelView):
		"""Creates JSON representation of the modelView including 
		field definitions, field values and actions"""
		definitions = [] 
		fieldValues = {}
		actions = []
		for group in modelView.superGroups:
			if (isinstance(group, fields.SuperGroup)):
				definitions.append(self.superGroup2Json(group, fieldValues))
			else:
				raise TypeError("The argument to 'groupList2Json' must be a list of SuperGroups" )
		
		if (modelView.actionBar is not None):
			for action in modelView.actionBar.actionList:
				actions.append(action.toJson())
		
		return {'definitions': definitions, 'values': fieldValues, 'actions': actions}

	def superGroup2Json(self, group, fieldValues):
		""""""
		jsonObject = {'type': 'SuperGroup', 'name': group._name, 'label': group.label}
		subgroupList = []
		for subgroup in group.groups:
			if (isinstance(subgroup, fields.FieldGroup)):
				subgroupList.append(self.fieldGroup2Json(subgroup, fieldValues))
			elif (isinstance(subgroup, fields.ViewGroup)):
				subgroupList.append(self.viewGroup2Json(subgroup, fieldValues))
			elif (isinstance(subgroup, fields.SuperGroup)):
				subgroupList.append(self.superGroup2Json(subgroup, fieldValues))
		jsonObject['groups'] = subgroupList				
		return jsonObject
		
	def fieldGroup2Json(self, group, fieldValues):
		""""""
		jsonObject = {'type': 'FieldGroup', 'name': group._name, 'label': group.label}
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__getattr__(field._name))
		jsonObject['fields'] = fieldList
		return jsonObject
				
	def viewGroup2Json(self, group, fieldValues):
		""""""
		jsonObject = {'type': 'ViewGroup', 'name': group._name, 'label': group.label}
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__getattr__(field._name))
		jsonObject['fields'] = fieldList
		return jsonObject
	
	
# 	def fieldValues2Json(self):
# 		jsonObject = {}
# 		for name, field in self.declared_fields.iteritems():
# 			jsonObject[name] = field.getValueRepr(self.__dict__[name])
# 		return jsonObject
	
	def fieldValuesFromJson(self, jsonDict):
		""""""
		for key, value in jsonDict.iteritems():
			field = self.declared_fields[key]
			self.__dict__[key] = field.parseValue(value)	

class ModelDocumentation(object):
	pass

class HtmlModule(object):
	pass