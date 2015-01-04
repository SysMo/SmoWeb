from smo.model.model import NumericalModel
from smo.model.fields import *
import numpy as np
from collections import OrderedDict

class TestModel(NumericalModel):
	############# Inputs ###############
	width = Quantity('Length')
	length = Quantity('Length')
	geometryIn = FieldGroup([width, length], label = "Geometry")
	
	inputs = SuperGroup([geometryIn], label = "Inputs")

	############# Results ###############
	area = Quantity('Area')
	geometryOut = FieldGroup([area], label = "Geometry")
	
	results = SuperGroup([geometryOut], label = "Results")
	
	############# Methods ###############
	def compute(self):
		self.area = self.width * self.length
	
	@classmethod
	def test(cls):
		t = TestModel()
		print t.testArray2
if __name__ == '__main__':
	TestModel.test()