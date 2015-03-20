import fields
from collections import OrderedDict
from smo.model.fields import FieldGroup, ViewGroup, ModelView
from smo.web.blocks import HtmlBlock, JsBlock
import smo.web.exceptions as E

class NumericalModelMeta(type):
	"""Metaclass facilitating the creation of a numerical
	model class. Collects all the declared fields in a 
	dictionary ``self.declared_fields``"""
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		if ('showOnHome' not in attrs):
			attrs['showOnHome'] = True
		if ('abstract' not in attrs):
			attrs['abstract'] = False
		# Collect fields from current class.
		current_fields = []
		current_submodels = []
		for key, value in list(attrs.items()):
			if isinstance(value, fields.SubModelGroup):
				current_submodels.append((key, value))
				value._name = key
				attrs.pop(key)
			elif isinstance(value, fields.Field):
				current_fields.append((key, value))
				value._name = key
				attrs.pop(key)
			elif isinstance(value, fields.Group):
				value._name = key
			elif isinstance(value, ModelView):
				value.name = key
			elif isinstance(value, HtmlBlock) or isinstance(value, JsBlock):
				value.name = key
				
		current_fields.sort(key=lambda x: x[1].creation_counter)
		current_submodels.sort(key=lambda x: x[1].creation_counter)
		attrs['declared_fields'] = OrderedDict(current_fields)
		attrs['declared_submodels'] = OrderedDict(current_submodels)
		attrs['declared_attrs'] = {}
		attrs['declared_attrs'].update(attrs['declared_fields'])
		attrs['declared_attrs'].update(attrs['declared_submodels'])
# 		current_groups.sort(key=lambda x: x[1].creation_counter)
# 		attrs['declared_groups'] = OrderedDict(current_groups)
		
		# Create the class type
		new_class = (super(NumericalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		# Collect fields from base classes
		base_fields = OrderedDict()
		base_submodels = OrderedDict()
		for c in reversed(new_class.__mro__[1:]):			
			if hasattr(c, 'declared_attrs'):
				# Checks for already declared fields in base classes
				for key in c.declared_attrs:
					if key in new_class.declared_attrs:
						raise AttributeError("Base class {0} already has attribute '{1}'.".format(c.__name__, key))
				base_fields.update(c.declared_fields)
				base_submodels.update(c.declared_submodels)
					
		new_class.declared_fields.update(base_fields)
		new_class.declared_submodels.update(base_submodels)
		
		# Resolving unresolved fields in field- and view-groups
		for key, value in new_class.__dict__.iteritems():
			if isinstance(value, FieldGroup) or isinstance(value, ViewGroup):
				for i in range(len(value.unresolved_fields)):
					unresolved_field = value.unresolved_fields[i]
					value.fields.append(new_class.declared_fields[unresolved_field])	
				del value.unresolved_fields[:]
		# Checking for obligatory attribute 'modelBlocks'
		if (name  != 'NumericalModel' and not new_class.abstract):
			if ('modelBlocks' not in new_class.__dict__):
				raise AttributeError("Page structure undefined. Class {0} must have attribute 'modelBlocks'.".format(name))
		
		return new_class

class NumericalModel(object):
	"""
	Abstract base class for numerical models.
	
	Class attributes:
		* :attr:`label`: label for the numerical model class (default is the numerical model class name), shows as title and thumbnail text for the model
		* :attr:`showOnHome`: used to specify if a thumbnail of the model is to show on the home page (default is True)
		* :attr:`figure`: ModelFigure object representing a figure, displayed on the page module of the model and on its thumbnail
		* :attr:`description`: ModelDescription object representing a description for the model, also used as tooltip of the model's thumbnail
		* :attr:`declared_fields`: OrderedDict containing the class attributes of type Field of the model
		* :attr:`modelBlocks`: (mandatory) list of blocks making up the model's page module. Block types may be: ModelView, HtmlBlock, JsBlock	
	"""

	__metaclass__ = NumericalModelMeta
	
	def __new__(cls, *args, **kwargs):
		"""Constructor for all numerical models. 
		Sets default values for all model fields"""
		self = object.__new__(cls)
		# Set default values to fields
		for name, field in self.declared_fields.iteritems():
			if (isinstance(field, (fields.RecordArray, fields.DataSeriesView))):
				self.__setattr__(name, field.default.copy())
			else:
				self.__setattr__(name, field.default)
		# Create submodel instances
		for name, submodel in self.declared_submodels.iteritems():
			if name in kwargs:
				params = kwargs.pop(name)
				instance = submodel.klass(**params)
			else:
				instance = submodel.klass()
			self.__dict__[name] = instance
		# Modify fields with values from the constructor
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
		"""
		Provides JSON serializaton of super-group 
		"""
		jsonObject = {'type': 'SuperGroup', 'name': group._name, 'label': group.label, 'show': group.show}
		subgroupList = []		
		for subgroup in group.groups:
			if (isinstance(subgroup, fields.SubModelGroup)):
				groupContent = self.subModelGroup2Json(subgroup, fieldValues)
			elif (isinstance(subgroup, fields.BasicGroup)):
				groupContent = self.basicGroup2Json(subgroup, fieldValues)
			else:
				raise TypeError("SuperGroup can only contain Field groups and View groups, not {}".format(type(subgroup)))
			subgroupList.append(groupContent)
		jsonObject['groups'] = subgroupList				
		return jsonObject
		
	def basicGroup2Json(self, group, fieldValues):
		"""
		Provides JSON serializaton of field-group and view-group 
		"""
		jsonObject = {'name': group._name, 'label': group.label, 'show': group.show}
		if (isinstance(group, FieldGroup)):
			jsonObject['type'] = 'FieldGroup'
		else:
			jsonObject['type'] = 'ViewGroup'
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__getattr__(field._name))
		jsonObject['fields'] = fieldList
		return jsonObject
	
	def subModelGroup2Json(self, group, fieldValues):
		"""
		Provides JSON serializaton of sub-model group
		"""
		instance = self.__getattr__(group._name)
		subFieldValues = {}
		jsonObject = instance.basicGroup2Json(group.group, subFieldValues)
		jsonObject['name'] = group._name
		if (group.label is not None):			
			jsonObject['label'] = group.label
		jsonObject['dataSourceRoot'] = group._name
		fieldValues[group._name] = subFieldValues
		return jsonObject
	
	def fieldValuesFromJson(self, jsonDict):
		"""
		Sets field values from dictionary representing JSON object
		"""
		for key, value in jsonDict.iteritems():
			if (key in self.declared_fields):
				field = self.declared_fields[key]
				self.__dict__[key] = field.parseValue(value)
			elif (key in self.declared_submodels):
				self.__getattr__(key).fieldValuesFromJson(value)
			else:
				raise E.FieldError('No field with name {} in model {}'.format(key, self.name)) 