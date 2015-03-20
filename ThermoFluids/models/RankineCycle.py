'''
Created on Mar 20, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.modules import RestModule
from smo.media.MaterialData import Fluids

class CycleComponent(NumericalModel):
	abstract = True

class ThermodynamicalCycle(NumericalModel):
	abstract = True
	
class Compressor(CycleComponent):
	modelType = Choices(OrderedDict((
		('S', 'isentropic'),
		('T', 'isothermal'),
	)), label = 'compressor model')
	eta = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency', show = "self.compressorModelType == 'S'")
	fQ = Quantity(default = 0, minValue = 0, maxValue = 1, label = 'heat loss factor', show="self.compressorModelType == 'S'")
	fg = FieldGroup([modelType, eta, fQ])
	modelBlocks = []

class RankineCycle(ThermodynamicalCycle):
	label = "Ranking cycle"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/ReverseBraytonCycle.svg")
	description = ModelDescription("Basic Rankine cycle used in power generation")
	
	#================ Inputs ================#
	#---------------- Fields ----------------#
	# FieldGroup
	fluidName = Choices(Fluids, default = 'R134a', label = 'fluid')	
	mDotRefrigerant = Quantity('MassFlowRate', default = (1, 'kg/min'), label = 'refrigerant flow rate')
	refrigerantInputs = FieldGroup([fluidName, mDotRefrigerant], 'Refrigerant')
	compressor = SubModelGroup(Compressor, Compressor.fg)
	
# 	# FieldGroup
# 	compressorModelType = Choices(OrderedDict((
# 		('S', 'isentropic'),
# 		('T', 'isothermal'),
# 	)), label = 'compressor model')
# 	etaCompressor = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency', show = "self.compressorModelType == 'S'")
# 	fQCompressor = Quantity(default = 0, minValue = 0, maxValue = 1, label = 'heat loss factor', show="self.compressorModelType == 'S'")
# 	compressorInputs = FieldGroup([compressorModelType, etaCompressor, fQCompressor], label = 'Compressor')
# 	# FieldGroup
# 	TCondensation = Quantity('Temperature', default = (40, 'degC'), label = 'condensation temperature')
# 	condenserOutletStateChoice = Choices(OrderedDict((
# 		('dT', 'sub-cooling'),
# 		('Q', 'vapor quality'),
# 		('eta', 'thermal efficiency'),
# 		('T', 'temperature'),
# 		('H', 'enthalpy'),
# 	)), label = 'compute outlet by')
# 	etaCondenser = Quantity(default = 0.9, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.condenserOutletStateChoice == "eta"')
# 	TExtCondenser = Quantity('Temperature', default = (30, 'degC'), label = 'external temperature', show = 'self.condenserOutletStateChoice == "eta"')
# 	dTOutletCondenser = Quantity('TemperatureDifference', default = (-5, 'degC'), minValue = -1e10, maxValue = -1e-3, label = 'outlet subcooling', show = 'self.condenserOutletStateChoice == "dT"')
# 	qOutletCondenser = Quantity(default = 0, minValue = 0, maxValue = 1, label = 'outlet vapor quality', show = 'self.condenserOutletStateChoice == "Q"')
# 	TOutletCondenser = Quantity('Temperature', default = (40, 'degC'), label = 'outlet temperature', show = 'self.condenserOutletStateChoice == "T"')
# 	hOutletCondenser = Quantity('SpecificEnthalpy', default = (100, 'kJ/kg'), minValue = -1e10, label = 'outlet enthalpy', show = 'self.condenserOutletStateChoice == "H"')
# 	
# 	condenserInputs = FieldGroup([TCondensation, condenserOutletStateChoice, etaCondenser, TExtCondenser, dTOutletCondenser, 
# 			TOutletCondenser, qOutletCondenser, hOutletCondenser], 
# 			label = 'Condensor')
# 
# 	# FieldGroup
# 	TEvaporation = Quantity('Temperature', default = (-10, 'degC'), label = 'evaporation temperature')
# 	evaporatorOutletStateChoice = Choices(OrderedDict((
# 		('dT', 'super-heating'),
# 		('Q', 'vapor quality'),
# 		('eta', 'thermal efficiency'),
# 		('T', 'temperature'),
# 		('H', 'enthalpy'),
# 	)), label = 'compute outlet by')
# 	etaEvaporator = Quantity(default = 0.9, label = 'thermal efficiency', minValue = 0, maxValue = 1, show = 'self.evaporatorOutletStateChoice == "eta"')
# 	TExtEvaporator = Quantity('Temperature', default = (0, 'degC'), label = 'external temperature', show = 'self.evaporatorOutletStateChoice == "eta"')
# 	dTOutletEvaporator = Quantity('TemperatureDifference', default = (5, 'degC'), minValue = 1e-3, maxValue = 1e10, label = 'outlet superheating', show = 'self.evaporatorOutletStateChoice == "dT"')
# 	qOutletEvaporator = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'outlet vapor quality', show = 'self.evaporatorOutletStateChoice == "Q"')
# 	TOutletEvaporator = Quantity('Temperature', default = (-10, 'degC'), label = 'outlet temperature', show = 'self.evaporatorOutletStateChoice == "T"')
# 	hOutletEvaporator = Quantity('SpecificEnthalpy', default = (100, 'kJ/kg'), minValue = -1e10, label = 'outlet enthalpy', show = 'self.evaporatorOutletStateChoice == "H"')
# 
# 	evaporatorInputs = FieldGroup([TEvaporation, evaporatorOutletStateChoice, etaEvaporator, TExtEvaporator, dTOutletEvaporator, 
# 			TOutletEvaporator, qOutletEvaporator, hOutletEvaporator], 
# 			label = 'Evaporator')
# 
# 	
# 	inputs = SuperGroup([refrigerantInputs, compressorInputs, condenserInputs, evaporatorInputs])
# 
# 	#---------------- Actions ----------------#
# 	computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
# 	inputActionBar = ActionBar([computeAction], save = True)
# 
# 	#--------------- Model view ---------------#
# 	inputView = ModelView(ioType = "input", superGroups = [inputs], 
# 		actionBar = inputActionBar, autoFetch = True)	
# 
# 	#================ Results ================#
# 	#---------------- Fields ----------------#
# 	cycleStatesTable = TableView((
# 		('T', Quantity('Temperature', default = (1, 'K'))),
# 		('p', Quantity('Pressure', default = (1, 'bar'))),
# 		('rho', Quantity('Density', default = (1, 'kg/m**3'))),
# 		('h', Quantity('SpecificEnthalpy', default = (1, 'kJ/kg'))),
# 		('s', Quantity('SpecificEntropy', default = (1, 'kJ/kg-K'))),
# 		('q', Quantity()),
# 		), label="Cycle states")
# 						
# 	cycleStates = ViewGroup([cycleStatesTable], label = "States")
# 	resultStates = SuperGroup([cycleStates], label="States")
# 	#---------------- Cycle diagram -----------#
# 	diagram = Image(default='', width=880, height=550)
# 	diagramViewGroup = ViewGroup([diagram], label = "P-H Diagram")
# 	resultDiagrams = SuperGroup([diagramViewGroup], label = "Diagrams")
# 	#---------------- Work/heat/mass flows -----------#
# 	compressorWork = Quantity('Power', default = (1, 'kW'), label = 'Compressor work')
# 	compressorHeat = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'Compressor heat out')
# 	condenserHeat = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'Condenser heat out')
# 	evaporatorHeat = Quantity('HeatFlowRate', default = (1, 'kW'), label = 'Evaporator heat in')
# 	flowFieldGroup = FieldGroup([compressorWork, compressorHeat, condenserHeat, evaporatorHeat], label = 'Energy flows')
# 	COPCooling = Quantity(label = 'COP cooling', description = 'COP when working in cooling mode')
# 	COPHeating = Quantity(label = 'COP heating', description = 'COP when working in heating mode')
# 	COPCarnotCooling = Quantity(label = 'COP Carnot cooling', description = 'COP (cooling) of Carnot cycle between the high (condenser) temperature and the low (evaporator) tempreature')
# 	COPCarnotHeating = Quantity(label = 'COP Carnot heating', description = 'COP (heating) of Carnot cycle between the high (condenser) temperature and the low (evaporator) tempreature')
# 	efficiencyFieldGroup = FieldGroup([COPCooling, COPHeating, COPCarnotCooling, COPCarnotHeating], 'Efficiency')
# 	resultFlows = SuperGroup([flowFieldGroup, efficiencyFieldGroup], label = 'Energy')
# 	#--------------- Model view ---------------#
# 	resultView = ModelView(ioType = "output", superGroups = [resultDiagrams, resultStates, resultFlows])

	#============= Page structure =============#
	#modelBlocks = [inputView, resultView]
	modelBlocks = []

	#================ Methods ================#	def compute(self):
	def compute(self):
		pass
	
def main():
	rc = RankineCycle()
# 	print rc.declared_fields
# 	print rc.declared_submodels
# 	print rc.declared_attrs
# 	print rc.compressor.eta

if __name__ == '__main__':
	main()