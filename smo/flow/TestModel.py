from smo.model.model import NumericalModel
from smo.model.fields import *
import numpy as np
from collections import OrderedDict

class TestModel(NumericalModel):
	############# Inputs ###############
	width = Quantity('Length')
	length = Quantity('Length')
	Tp_array = RecordArray(OrderedDict((
					('temperature', Quantity('Temperature')),
					('pressure', Quantity('Pressure')),	   
				)), numRows=5, label = "Tp state array")
	
	geometryIn = FieldGroup([width, length], label = "Geometry")
	flowIn = FieldGroup([Tp_array], label = "Flow")
	
	inputs = SuperGroup([geometryIn, flowIn], label = "Inputs")

	############# Results ###############
	area = Quantity('Area')
	isTurblent = Boolean(default = False, label = "turbulent flow")
	
	geometryOut = FieldGroup([area], label = "Geometry")
	flowOut = FieldGroup([isTurblent], label = "Flow")
	
	results = SuperGroup([geometryOut, flowOut], label = "Results")
	
	############# Methods ###############
	def compute(self):
		self.area = self.width * self.length
	
	@classmethod
	def test(cls):
		t = TestModel()
		print t.testArray2
if __name__ == '__main__':
	TestModel.test()