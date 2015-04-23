'''
Created on Apr 2, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from smo.model.model import NumericalModel
from ThermoFluids.tasks import compute1

class ABC(NumericalModel):
	showOnHome = False
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
		res1 = compute1.delay()
		print res1.id
		