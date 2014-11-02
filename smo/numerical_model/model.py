from fields import Field, Quantity, Group, FieldGroup, SuperGroup
from collections import OrderedDict

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
			instance.__setattr__(name, field.default)  
		for name, value in kwargs.iteritems():
			instance.__setattr__(name, value)
		return instance
	
	def __setattr__(self, name, value):
		if name in self.declared_fields.keys():
			object.__setattr__(self, name, self.declared_fields[name].setValue(value))
		else:
			raise AttributeError("Class '{0}' has no field '{1}'".format(self.__class__.__name__, name))
			
	def group2Json(self, group):
		if (isinstance(group, FieldGroup)):
			return self.fieldGroup2Json(group)
		elif (isinstance(group, SuperGroup)):
			return self.superGroup2Json(group)
	
	def fieldGroup2Json(self, group):
		jsonObject = {'type': 'FieldGroup', 'name': group._name, 'label': group.label}
		fieldList = []
		for field in group.fields:
			fieldDict = {'name' : field._name, 'label': field.label}
			if (isinstance(field, Quantity)):
				fieldDict['type'] = 'Quantity'
				fieldDict['quantity'] = field.type
				fieldDict['defaultDispUnit'] = field.defaultDispUnit
				fieldDict['value'] = self.__dict__[field._name]
			fieldList.append(fieldDict)
		jsonObject['fields'] = fieldList
		return jsonObject
				
	def superGroup2Json(self, group):
		jsonObject = {'type': 'SuperGroup', 'name': group._name, 'label': group.label}
		subgroupList = []
		for subgroup in group.groups:
			if (isinstance(subgroup, FieldGroup)):
				subgroupList.append(self.fieldGroup2Json(subgroup))
			elif (isinstance(subgroup, SuperGroup)):
				subgroupList.append(self.superGroup2Json(subgroup))
		jsonObject['groups'] = subgroupList				
		return jsonObject
