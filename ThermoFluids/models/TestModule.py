'''
Created on Apr 2, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from smo.model.model import NumericalModel
from ThermoFluids.tasks import doSomething 

class ABC(NumericalModel):
	label = 'ABC'
	compressor = F.SubModelGroup(TC.Compressor, ['etaS', 'fQ', 'modelType'], label = 'Compressor') #fields = )
	inputs = F.SuperGroup([compressor])
	inputView = F.ModelView(ioType = "input", superGroups = [inputs], autoFetch = True)
	resultView = F.ModelView(ioType = "output", superGroups = [])
	modelBlocks = [inputView, resultView]
	
	def __init__(self):
		self.compressor.modelType = 'S'
		self.compressor.declared_fields['modelType'].show = 'false'
		
	def compute(self):
		print("Trying to start task")
		result = doSomething.delay('ivcho')
		print("Suceeded to start task")
		#r = result.ready()
		#print("Finished: {}".format(r))
		r = result.get(timeout=4)
		print(r)
		print(result.ready())
