import fields
from collections import OrderedDict
from smo.model.fields import FieldGroup, ViewGroup, ModelView 
from smo.web.blocks import HtmlBlock, JsBlock

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
			elif isinstance(value, HtmlBlock) or isinstance(value, JsBlock):
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
		
		# Checking for obligatory attribute 'modelBlocks'
		if (name  != 'NumericalModel'):
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
		"""
		Provides JSON serializaton of super-group 
		"""
		jsonObject = {'type': 'SuperGroup', 'name': group._name, 'label': group.label, 'show': group.show}
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
		"""
		Provides JSON serializaton of field-group 
		"""
		jsonObject = {'type': 'FieldGroup', 'name': group._name, 'label': group.label, 'show': group.show}
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__getattr__(field._name))
		jsonObject['fields'] = fieldList
		return jsonObject
				
	def viewGroup2Json(self, group, fieldValues):
		"""
		Provides JSON serializaton of view-group 
		"""
		jsonObject = {'type': 'ViewGroup', 'name': group._name, 'label': group.label, 'show': group.show}
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__getattr__(field._name))
		jsonObject['fields'] = fieldList
		return jsonObject
	
# Left if needed in the future	
# 	def fieldValues2Json(self):
# 		jsonObject = {}
# 		for name, field in self.declared_fields.iteritems():
# 			jsonObject[name] = field.getValueRepr(self.__dict__[name])
# 		return jsonObject
	
	def fieldValuesFromJson(self, jsonDict):
		"""
		Sets field values from dictionary representing JSON object
		"""
		for key, value in jsonDict.iteritems():
			field = self.declared_fields[key]
			self.__dict__[key] = field.parseValue(value)