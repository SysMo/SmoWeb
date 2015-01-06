from smo.model.model import NumericalModel, ModelView, ModelDocumentation
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
import numpy as np
from collections import OrderedDict

class AreaCalculator(NumericalModel):
	name = "AreaCalculator"
	label = "Area Calculator"
	############# Inputs ###############
	# Fields
	width = Quantity('Length', label='width')
	length = Quantity('Length', label='length')
	geometryIn = FieldGroup([width, length], label = "Geometry")
	
	compositePipe = RecordArray(
        OrderedDict((
                ('name', String(maxLength = 20)),
                ('length', Quantity('Length')),
                ('diameter', Quantity('Length')),          
        )), numRows = 3, label='composite pipe')
	
	flowIn = FieldGroup([compositePipe], label = 'Flow')
	
	inputs = SuperGroup([geometryIn, flowIn], label = "Inputs")
	
	# Actions
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	blahAction = ServerAction("blah", label = "Blah", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction, blahAction], save = True)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	area = Quantity('Area')
	geometryOut = FieldGroup([area], label = "Geometry")
	
	results = SuperGroup([geometryOut], label = "Results")

	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	############# Methods ###############
	def compute(self):
		self.area = self.width * self.length

class AreaCalculatorDoc(ModelDocumentation):
	name = 'AreaCalculatorDoc'
	label = 'Area Calculator (Docs)'
	template = 'documentation/html/AreaCalculatorDoc.html'
