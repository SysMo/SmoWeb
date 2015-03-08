'''
Created on Feb 25, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
from collections import OrderedDict
from docutils.utils.math.math2html import ParameterDefinition

class Causality(object):
	parameter = 0
	calculatedParameter = 1
	input = 2
	output = 3
	local = 4
	independent = 5
	
class Variability(object):
	constant = 0
	fixed = 1
	tunable = 2
	discrete = 3
	continuous = 4

class ScalarVariable(object):
	"""
	Abstract base class for all the variable types.
	"""
	# Tracks each time an instance is created. Used to retain order.
	creation_counter = 0
	
	def __init__(self, causality, variability, label = None, description = None, **kwargs):
		"""
	 	:param str label: the text label used in the user interface usually in front of the field
	 	:param str description: description to show as tooltip when hovering over the field label
		"""
		
		self.label = label
		self.description = description
		self.causality = causality
		self.variability = variability
			
		# Increase the creation counter, and save our local copy.
		self.creation_counter = ScalarVariable.creation_counter
		ScalarVariable.creation_counter += 1
	
	def setName(self, name):
		self.name = name
		if (self.label is None):
			self.label = self.name
		if (self.description is None):
			self.description = self.label

class RealVariable(ScalarVariable):
	def __init__(self, **kwargs):
		super(RealVariable, self).__init__(**kwargs)

class RealState(RealVariable):
	def __init__(self, **kwargs):
		super(RealState, self).__init__(**kwargs)

class DynamicalModelMeta(type):
	def __new__(cls, name, bases, attrs):
		# Label
		if ('label' not in attrs):
			attrs['label'] = name
		# Collect fields from current class.
		current_variables = []
		for key, value in attrs.items():
			if isinstance(value, ScalarVariable):
				current_variables.append((key, value))
				value.setName(key)
				attrs.pop(key)
				
		current_variables.sort(key=lambda x: x[1].creation_counter)
		attrs['_variables'] = OrderedDict(current_variables)

		new_class = (super(DynamicalModelMeta, cls)
			.__new__(cls, name, bases, attrs))
		
		return new_class
	
class DynamicalModel(object):
	__metaclass__ = DynamicalModelMeta

		