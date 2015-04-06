'''
Created on Apr 2, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
import lib.ThermodynamicComponents as TC
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar

class ABC(NumericalModel):
	label = 'ABC'
	compressor = F.SubModelGroup(TC.Compressor, ['etaS', 'fQ', 'modelType'], label = 'Compressor') #fields = )
	inputs = F.SuperGroup([compressor])
	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	inputView = F.ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	resultView = F.ModelView(ioType = "output", superGroups = [])
	modelBlocks = [inputView, resultView]
	
	def __init__(self):
		self.compressor.modelType = 'S'
		self.compressor.declared_fields['modelType'].show = 'false'
		
	def compute(self):
		print self.compressor.modelType
		print self.compressor.etaS
		print self.compressor.fQ