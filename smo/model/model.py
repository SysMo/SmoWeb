from fields import Field, Quantity, Group, FieldGroup, ViewGroup, RecordArray, SuperGroup
from collections import OrderedDict
import copy

#TODO: Currently inheritance not supported
class NumericalModelMeta(type):
	def __new__(cls, name, bases, attrs):
		# Collect fields from current class.
		current_fields = []
		current_groups = []
		for key, value in list(attrs.items()):
			if isinstance(value, Field):
				current_fields.append((key, value))
				value._name = key
				attrs.pop(key)
			elif isinstance(value, Group):
				current_groups.append((key, value))
				value._name = key
				
		current_fields.sort(key=lambda x: x[1].creation_counter)
		attrs['declared_fields'] = OrderedDict(current_fields)
		current_groups.sort(key=lambda x: x[1].creation_counter)
		attrs['declared_groups'] = OrderedDict(current_groups)

		new_class = (super(NumericalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
# 		# Walk through the MRO.
# 		declared_fields = OrderedDict()
# 		for base in reversed(new_class.__mro__):
# 			# Collect fields from base class.
# 			if hasattr(base, 'declared_fields'):
# 				declared_fields.update(base.declared_fields)
# 
# 			# Field shadowing.
# 			for attr, value in base.__dict__.items():
# 				if value is None and attr in declared_fields:
# 					declared_fields.pop(attr)
# 
# 		new_class.base_fields = declared_fields
# 		new_class.declared_fields = declared_fields

		return new_class

class NumericalModel(object):
	__metaclass__ = NumericalModelMeta
	
	def __new__(cls, *args, **kwargs):
		instance = object.__new__(cls)
		for name, field in instance.declared_fields.iteritems():
			if (isinstance(object, RecordArray)):
				instance.__setattr__(name, field.default.copy())
			else:
				instance.__setattr__(name, field.default)  
		for name, value in kwargs.iteritems():
			instance.__setattr__(name, value)
		return instance
	
	def __setattr__(self, name, value):
		if name in self.declared_fields.keys():
			object.__setattr__(self, name, self.declared_fields[name].parseValue(value))
		else:
			raise AttributeError("Class '{0}' has no field '{1}'".format(self.__class__.__name__, name))
	
	def superGroupList2Json(self, groupList):
		definitions = [] 
		fieldValues = {}
		for group in groupList:
			if (isinstance(group, SuperGroup)):
				definitions.append(self.superGroup2Json(group, fieldValues))
			else:
				raise TypeError("The argument to 'groupList2Json' must be a list of SuperGroups" )
		
		return {'definitions': definitions, 'values': fieldValues}

	def superGroup2Json(self, group, fieldValues):
		jsonObject = {'type': 'SuperGroup', 'name': group._name, 'label': group.label}
		subgroupList = []
		for subgroup in group.groups:
			if (isinstance(subgroup, FieldGroup)):
				subgroupList.append(self.fieldGroup2Json(subgroup, fieldValues))
			elif (isinstance(subgroup, ViewGroup)):
				subgroupList.append(self.viewGroup2Json(subgroup, fieldValues))
			elif (isinstance(subgroup, SuperGroup)):
				subgroupList.append(self.superGroup2Json(subgroup, fieldValues))
		jsonObject['groups'] = subgroupList				
		return jsonObject
		
	def fieldGroup2Json(self, group, fieldValues):
		jsonObject = {'type': 'FieldGroup', 'name': group._name, 'label': group.label}
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__dict__[field._name])
		jsonObject['fields'] = fieldList
		return jsonObject
				
	def viewGroup2Json(self, group, fieldValues):
		jsonObject = {'type': 'ViewGroup', 'name': group._name, 'label': group.label}
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field._name] = field.getValueRepr(self.__dict__[field._name])
		jsonObject['fields'] = fieldList
		return jsonObject
	
	
# 	def fieldValues2Json(self):
# 		jsonObject = {}
# 		for name, field in self.declared_fields.iteritems():
# 			jsonObject[name] = field.getValueRepr(self.__dict__[name])
# 		return jsonObject
	
	def fieldValuesFromJson(self, jsonDict):
		for key, value in jsonDict.iteritems():
			field = self.declared_fields[key]
			self.__dict__[key] = field.parseValue(value)