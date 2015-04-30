import fields
from collections import OrderedDict
from smo.model.fields import FieldGroup, BasicGroup, ModelView, SuperGroup
from smo.web.blocks import HtmlBlock, JsBlock
import smo.web.exceptions as E
from smo.model.actions import ServerAction

class NumericalModelMeta(type):
	"""Metaclass facilitating the creation of a numerical
	model class. Collects all declared fields, submodels, basic groups, supergroups and model views in 
	the class in respective dictionaries"""
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		if ('showOnHome' not in attrs):
			attrs['showOnHome'] = True
		if ('async' not in attrs):
			attrs['async'] = False
		if (attrs['async'] == True):
			if ('progressOptions' not in attrs):
				attrs['progressOptions'] = {'suffix': '%', 'fractionOutput': False}
		if ('abstract' not in attrs):
			attrs['abstract'] = False
		# Collect fields from current class.
		current_fields = []
		current_submodels = []
		current_basicGroups = {}
		current_superGroups = {}
		current_modelViews = {}
		current_ports = {}
		for key, value in list(attrs.items()):
			if isinstance(value, fields.SubModelGroup):
				current_submodels.append((key, value))
				if (isinstance(value.group, BasicGroup)):
					current_basicGroups[key] = value
				elif (isinstance(value.group, SuperGroup)):
					current_superGroups[key] = value
				else:
					raise TypeError ('The submodel group {} in class {} must be either field or view group'.format(key, name))
				value.name = key
				attrs.pop(key)
			elif isinstance(value, fields.Port):
				current_ports[key] = value
				value.name = key
				attrs.pop(key)
			elif isinstance(value, fields.Field):
				current_fields.append((key, value))
				value.name = key
				attrs.pop(key)
			elif isinstance(value, fields.BasicGroup):
				value.name = key
				current_basicGroups[key] = value
				attrs.pop(key)
			elif isinstance(value, fields.SuperGroup):
				value.name = key
				current_superGroups[key] = value
				attrs.pop(key)
			elif isinstance(value, fields.Group):
#				value.name = key
#				attrs.pop(key)
				raise TypeError('Unknown group type')
			elif isinstance(value, ModelView):
				value.name = key
				current_modelViews[key] = value
				attrs.pop(key)
			elif isinstance(value, HtmlBlock) or isinstance(value, JsBlock):
				value.name = key
				
		current_fields.sort(key=lambda x: x[1].creation_counter)
		current_submodels.sort(key=lambda x: x[1].creation_counter)
		# Fields
		attrs['declared_fields'] = OrderedDict(current_fields)
		attrs['declared_submodels'] = OrderedDict(current_submodels)
		attrs['declared_attrs'] = {}
		attrs['declared_attrs'].update(attrs['declared_fields'])
		attrs['declared_attrs'].update(attrs['declared_submodels'])
		attrs['declared_ports'] = current_ports
		# Groups
		attrs['declared_basicGroups'] = current_basicGroups
		attrs['declared_superGroups'] = current_superGroups
		attrs['declared_modelViews'] = current_modelViews
		
		# Create the class type
		klass = (super(NumericalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		# Collect fields from base classes
		base_fields = OrderedDict()
		base_submodels = OrderedDict()
		base_basicGroups = {}
		base_superGroups = {}
		base_modelViews = {}
		base_ports = {}
		# It should not be necessary to walk the complete MRO. Just the bases should be enough
		# as they have already collected all the fields from their ancesstors
		#for base in reversed(klass.__mro__[1:]):
		for base in klass.__bases__:
			if not (hasattr(base, 'declared_attrs')):
				continue			
			# Collect declared fields from base classes
			for key in base.declared_attrs:
				if key in klass.declared_attrs:
					raise AttributeError("Base class {0} defines attribute '{1}', which class {2} attempts to redefine".format(base.__name__, key, name))
				elif (key in base_fields or key in base_submodels):
					raise AttributeError("Attribute {} in class {} already inherited. Attempt to inherit it again from another base class {}.".format(key, name, base.__name__))
			base_fields.update(base.declared_fields)
			base_submodels.update(base.declared_submodels)
			
			# Collect declared ports from base classes
			for key, value in base.declared_ports.iteritems():
				if key in klass.declared_ports:
					raise AttributeError("Base class {0} defines port '{1}', which class {2} attempts to redefine".format(base.__name__, key, name))
				elif (key in base_ports):
					raise AttributeError("Port {} in class {} already inherited. Attempt to inherit it again from another base class {}.".format(key, name, base.__name__))
				base_ports[key] = value
				
			# Collect declared field and view groups from base classes
			for key, value in base.declared_basicGroups.iteritems():
				if (key in klass.declared_basicGroups):
					# The group is redefined in the new class, so don't inherit it
					pass
				else:
					if (key not in base_basicGroups):
						base_basicGroups[key] =  value.copyByName()
					else:
						raise AttributeError("Group {} in class {} already inherited. Attempt to inherit it again from base class {}.".format(key, name, base.__name__))

			# Collect declared super-groups from base classes
			for key, value in base.declared_superGroups.iteritems():
				if (key in klass.declared_superGroups):
					# The group is redefined in the new class, so don't inherit it
					pass
				else:
					if (key not in base_superGroups):
						base_superGroups[key] =  value.copyByName()
					else:
						raise AttributeError("Group {} in class {} already inherited. Attempt to inherit it again from base class {}.".format(key, name, base.__name__))

			# Collect declared model-views from base classes
			for key, value in base.declared_modelViews.iteritems():
				if (key in klass.declared_modelViews):
					# The group is redefined in the new class, so don't inherit it
					pass
				else:
					if (key not in base_modelViews):
						base_modelViews[key] =  value.copyByName()
					else:
						raise AttributeError("ModelView {} in class {} already inherited. Attempt to inherit it again from base class {}.".format(key, name, base.__name__))

		klass.declared_fields.update(base_fields)
		klass.declared_submodels.update(base_submodels)
		klass.declared_attrs.update(base_fields)
		klass.declared_attrs.update(base_submodels)
		klass.declared_basicGroups.update(base_basicGroups)
		klass.declared_superGroups.update(base_superGroups)
		klass.declared_modelViews.update(base_modelViews)
		klass.declared_ports.update(base_ports)
		# Resolving fields in field- and view-groups by name
		for value in klass.declared_basicGroups.itervalues():
			if (isinstance(value, BasicGroup)): # Could be submodel group
				value.resolve(klass.declared_fields)
		
		#Resolving field groups, view groups or submodel groups by name
		for value in klass.declared_superGroups.itervalues():
			if (isinstance(value, SuperGroup)):
				value.resolve(klass.declared_basicGroups)

		# Resolving supergroups by name
		for value in klass.declared_modelViews.itervalues():
			value.resolve(klass.declared_superGroups)
												
		# Checking for obligatory attribute 'modelBlocks'
		if (name  != 'NumericalModel' and not klass.abstract):			
			if ('modelBlocks' not in klass.__dict__):
				modelBlocks = None
				for base in klass.__bases__:
					if hasattr(base, 'modelBlocks'):
						modelBlocks = [block.name if isinstance(block, ModelView) else block for block in base.modelBlocks]
				if (modelBlocks is None):
					raise AttributeError("Page structure undefined. Class {0} must have attribute 'modelBlocks' or must inherit it from a base class.".format(name))
				else:
					klass.modelBlocks = modelBlocks
			for i in range(len(klass.modelBlocks)):
				# Then resolve them to the ModelViews from the current model 
				if (isinstance(klass.modelBlocks[i], basestring)):
					klass.modelBlocks[i] = klass.declared_modelViews[klass.modelBlocks[i]]
			#print("NumericalModel class: {}, {}".format(name, [modelBlock.name for modelBlock in klass.modelBlocks])) 
		return klass

class NumericalModel(object):
	"""
	Abstract base class for numerical models.
	
	Class attributes:
		* :attr:`label`: label for the numerical model class (default is the numerical model class name), shows as title and thumbnail text for the model
		* :attr:`showOnHome`: used to specify if a thumbnail of the model is to show on the home page (default is True)
		* :attr:`figure`: ModelFigure object representing a figure, displayed on the page module of the model and on its thumbnail
		* :attr:`description`: ModelDescription object representing a description for the model, also used as tooltip of the model's thumbnail
		* :attr:`declared_fields`: OrderedDict containing the fields declared in the model
		* :attr:`declared_submodels`: OrderedDict containing the submodels declared in the model
		* :attr:`declared_attrs`: dictionary containing the declared fields and submodels
		* :attr:`declared_basicGroups`: dictionary containing the field-groups and view-groups declared in the model
		* :attr:`declared_superGroups`: dictionary containing the supergroups declared in the model
		* :attr:`declared_modelViews`: dictionary containing the declared model views
		* :attr:`modelBlocks`: (mandatory) list of blocks making up the model's page module. Block types may be: ModelView, HtmlBlock, JsBlock	
	"""

	__metaclass__ = NumericalModelMeta
	
	def __new__(cls, *args, **kwargs):
		"""Constructor for all numerical models. 
		Sets default values for all model fields"""
		self = object.__new__(cls)
		# Set default values to fields
		for name, field in self.declared_fields.iteritems():
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
		# Create port instances
		for name, port in self.declared_ports.iteritems():
			self.__dict__[name] = port.klass()
		return self
	
	def __setattr__(self, name, value):
		"""Sets field value using the :func:`Field.parseValue` method"""
		if name in self.declared_fields.keys():
			object.__setattr__(self, name, self.declared_fields[name].parseValue(value))
		else:
			object.__setattr__(self, name, value)
			#raise AttributeError("Class '{0}' has no field '{1}'".format(self.__class__.__name__, name))
	
	def __getattr__(self, name):
		return object.__getattribute__(self, name)
	
	def redefineField(self, fieldName, basicGroupName, newField):
		newField.name = fieldName
		i = self.declared_basicGroups[basicGroupName].fields.index(self.declared_fields[fieldName])
		self.declared_basicGroups[basicGroupName].fields[i] = newField
		self.declared_fields[fieldName] = newField
	
	def modelView2Json(self, modelView):
		"""Creates JSON representation of the modelView including 
		field definitions, field values and actions"""
		if (isinstance(modelView, basestring)):
			modelView = self.declared_modelViews[modelView]
		definitions = [] 
		fieldValues = {}
		actions = []
		for group in modelView.superGroups:
			if (isinstance(group, fields.SubModelGroup)):
				groupContent = self.subModelGroup2Json(group, fieldValues)
			elif (isinstance(group, fields.SuperGroup)):
				groupContent = self.superGroup2Json(group, fieldValues)
			else:
				raise TypeError("The argument to 'groupList2Json' must be a list of SuperGroups" )		
			definitions.append(groupContent)
		if (modelView.actionBar is not None):
			for action in modelView.actionBar.actionList:
				actions.append(action.toJson())
		return {'definitions': definitions, 'values': fieldValues, 'actions': actions, 
					'keepDefaultDefs': modelView.keepDefaultDefs, 'computeAsync' : self.async}

	def superGroup2Json(self, group, fieldValues):
		"""
		Provides JSON serializaton of super-group 
		"""
		jsonObject = {'type': 'SuperGroup', 'name': group.name, 'label': group.label}
		if (group.show is not None):
			jsonObject['show'] = group.show
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
		jsonObject = {'name': group.name, 'label': group.label}
		if (group.show is not None):
			jsonObject['show'] = group.show
		jsonObject['hideContainer'] = group.hideContainer
		if (isinstance(group, FieldGroup)):
			jsonObject['type'] = 'FieldGroup'
		else:
			jsonObject['type'] = 'ViewGroup'
		fieldList = []
		for field in group.fields:
			fieldList.append(field.toFormDict())
			fieldValues[field.name] = field.getValueRepr(self.__getattr__(field.name))
		jsonObject['fields'] = fieldList
		return jsonObject
	
	def subModelGroup2Json(self, group, fieldValues):
		"""
		Provides JSON serializaton of sub-model group
		"""
		instance = self.__getattr__(group.name)
		subFieldValues = {}
		if (isinstance(group.group, BasicGroup)):
			jsonObject = instance.basicGroup2Json(group.group, subFieldValues)
		elif (isinstance(group.group, SuperGroup)):
			jsonObject = instance.superGroup2Json(group.group, subFieldValues)
		else:
			pass			
		jsonObject['name'] = group.name
		if (group.label is not None):			
			jsonObject['label'] = group.label
		if (group.show is not None):
			jsonObject['show'] = group.show
		jsonObject['dataSourceRoot'] = group.name
		fieldValues[group.name] = subFieldValues
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
	
	def updateProgress(self, current, total): 
		self.task.update_state(state='PROGRESS', 
									meta={'current': current, 'total': total})
