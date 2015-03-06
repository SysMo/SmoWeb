'''
Created on Nov 05, 2014
@author: Atanas Pavlov
'''
from collections import OrderedDict
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.web.blocks import HtmlBlock
from smo.web.modules import RestModule
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from smo.media.MaterialData import Fluids
from smo.media.CoolProp.CoolPropReferences import References
from smo.media.diagrams.StateDiagrams import PHDiagram, PHDiagramFluids

import os
from pymongo import MongoClient
from bson.objectid import ObjectId
mongoClient = MongoClient()
db = mongoClient.SmoWeb
coll = db["PropertyCalculatorCoolprop"]


StateVariableOptions = OrderedDict((
	('P', 'pressure (P)'),
	('T', 'temperature (T)'),
	('D', 'density (D)'),
	('H', 'specific enthalpy (H)'),
	('S', 'specific entropy (S)'),
	('Q', 'vapor quality (Q)')
	))

referenceKeys = OrderedDict((
	('EOS', 'Equation of State'), 
	('CP0', 'CP0 reference'),
	('VISCOSITY', 'Viscosity'),
	('CONDUCTIVITY', 'Conductivity'),
	('ECS_LENNARD_JONES', 'Lennard-Jones Parameters for ECS'),
	('ECS_FITS', 'ECS_FITS reference'),
	('SURFACE_TENSION', 'Surface Tension')
	))

class PropertyCalculatorCoolprop(NumericalModel):
	label = "Property calculator"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/CoolPropLogo.png", width=150)
	description = ModelDescription(
		'A fluid properties calculator for liquid, vapor and super-critical states, \
		based on the open source thermodynamic package <a href="http://www.coolprop.org/" >CoolProp</a>', 
		asTooltip ='A fluid properties calculator for liquid, vapor and super-critical states, \
		based on the open source thermodynamic package CoolProp', show = True)
	showOnHome = True
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')	
	stateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
	p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure',show="self.stateVariable1 == 'P'")
	T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
	rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
	h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), minValue = -1e99, label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
	s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), minValue = -1e99, label = 'specific entropy', show="self.stateVariable1 == 'S'")
	q1 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable1 == 'Q'")
	stateVariable2 = Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
	p2 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
	T2 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
	rho2 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
	h2 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), minValue = -1e99, label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
	s2 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), minValue = -1e99, label = 'specific entropy', show="self.stateVariable2 == 'S'")
	q2 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable2 == 'Q'")
	####
	stateGroup1 = FieldGroup([fluidName], label = 'Fluid')
	stateGroup2 = FieldGroup([stateVariable1, p1, T1, rho1, h1, s1, q1, stateVariable2, p2, T2, rho2, h2, s2, q2], label = 'States')
	inputs = SuperGroup([stateGroup1, stateGroup2], label = "Inputs")
	
	# Actions
	computeAction = ServerAction("computeFluidProps", label = "Compute", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = True)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	recordId = String('', show="false")
	T = Quantity('Temperature', label = 'temperature')
	p = Quantity('Pressure', label = 'pressure')
	rho = Quantity('Density', label = 'density')
	h = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
	s = Quantity('SpecificEntropy', label = 'specific entropy')
	q = Quantity('VaporQuality', label = 'vapor quality')
	u = Quantity('SpecificInternalEnergy', label = 'specific internal energy')
	#####
	cp = Quantity('SpecificHeatCapacity', label = 'heat capacity (cp)')
	cv = Quantity('SpecificHeatCapacity', label = 'heat capacity (cv)')	
	gamma = Quantity('Dimensionless', label = 'gamma = cp/cv')
# 	beta = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
# 	alpha = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
	Pr = Quantity('Dimensionless', label = 'Prandtl number')
	cond = Quantity('ThermalConductivity', label = 'thermal conductivity')
	mu = Quantity('DynamicViscosity', label = 'dynamic viscosity')
	dpdT_v = Quantity('Dimensionless', label = '(dp/dT)<sub>v</sub>')
	dpdv_T = Quantity('Dimensionless', label = '(dp/dv)<sub>T</sub>')
	#####
	stateVariablesResults = FieldGroup([recordId, T, p, rho, h, s, q, u], label = 'States')
	derivativeResults = FieldGroup([cp, cv, gamma, Pr, cond, mu, dpdT_v, dpdv_T], label = 'Derivatives & Transport')
	props = SuperGroup([stateVariablesResults, derivativeResults], label = "Properties")
	#####
	rho_L = Quantity('Density', label = 'density')
	h_L = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
	s_L = Quantity('SpecificEntropy', label = 'specific entropy')	
	#####
	rho_V = Quantity('Density', label = 'density')
	h_V = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
	s_V = Quantity('SpecificEntropy', label = 'specific entropy')
	#####
	isTwoPhase = Boolean(label = 'is two phase')
	liquidResults = FieldGroup([rho_L, h_L, s_L], label="Liquid")
	vaporResults = FieldGroup([rho_V, h_V, s_V], label="Vapor")
	saturationProps = SuperGroup([liquidResults, vaporResults], label="Phases")
	#####
	paramVarTable = TableView(label="Variation Table", dataLabels = ['T', 'p', 'rho', 'h', 'q', 'u', 'cp', 'cv', 'lambda', 'mu'], 
							quantities = ['Temperature', 'Pressure', 'Density', 'SpecificEnthalpy', 'VaporQuality', 'SpecificEnergy',
										 'SpecificHeatCapacity', 'SpecificHeatCapacity', 'ThermalConductivity', 'DynamicViscosity'],
							options = {'formats': ['0.000', '0.000E0', '0.000', '0.000E0', '0.00', '0.000E0', '0.000E0', '0.000E0', '0.000E0', '0.000E0']})
	
# 	testVarTable = VariationTable(label="Variation Table", dataLabels = ['T', 'p', 'h'], 
# 							visibleColumns = [1,2], quantities = ['Temperature', 'Pressure', 'SpecificEnthalpy'],
# 							options = {'formats': ['0.0000E0', '0.000', '0.000']},
# 							parentCollection = coll,
# 							fieldName = "testVarTable")
	
	paramVariation = ViewGroup([paramVarTable], label="Parameter Variation")
	FluidPoints = SuperGroup([paramVariation], label = "Fluid Points")	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [props, FluidPoints])
	resultViewIsTwoPhase = ModelView(ioType = "output", superGroups = [props, saturationProps, FluidPoints])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView, resultViewIsTwoPhase]

	############# Methods ###############	
	def getStateValue(self, sVar, index):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[sVarDict[sVar]+str(index)]
			
	def compute(self):
		fState = FluidState(self.fluidName)
		fState.update(self.stateVariable1, self.getStateValue(self.stateVariable1, 1), 
						self.stateVariable2, self.getStateValue(self.stateVariable2, 2))
		self.T = fState.T
		self.p = fState.p
		self.rho = fState.rho
		self.h = fState.h
		self.s = fState.s
		self.q = fState.q
		self.u = fState.u
		
		self.cp = fState.cp
		self.cv = fState.cv
		self.gamma = fState.gamma
		self.Pr = fState.Pr
		self.cond = fState.cond
		self.mu = fState.mu
		self.dpdT_v = fState.dpdT_v
		self.dpdv_T = fState.dpdv_T
		
		self.isTwoPhase = fState.isTwoPhase()
		if (self.isTwoPhase == True):
			satL = fState.SatL
			satV = fState.SatV

			self.rho_L = satL.rho
			self.h_L = satL.h
			self.s_L = satL.s
			
			self.rho_V = satV.rho
			self.h_V = satV.h
			self.s_V = satV.s
		
# 		self.testVarTable = VariationTableValue(recordId = self.recordId, 
# 											newRow = [self.T, self.p, self.h],
# 											collection = coll["testVarTable"],
# 											varTableName = "testVarTable")
# 		
# 		self.recordId = self.testVarTable.recordId
		

		self.computeParamVarTable('paramVarTable', 'recordId', ['T', 'p', 'rho', 'h', 'q', 'u', 'cp', 'cv', 'cond', 'mu'])
		
	def computeParamVarTable(self, tableName, recordId, paramNames):
		db = mongoClient.SmoWeb
		coll = db[self.__class__.__name__]
		numCol = len(paramNames)
		if (self.__getattr__(recordId) != ''):			
			record = coll.find_one({"_id": ObjectId(self.__getattr__(recordId))})
			if (record is not None):
				recordValues = record[tableName]
				numRows = len(recordValues)
				self.__setattr__(tableName, np.zeros((numRows + 1, numCol)))
				self.__getattr__(tableName)[0:numRows] = np.array(recordValues)
				self.__getattr__(tableName)[numRows] = np.array([self.__getattr__(paramName) for paramName in paramNames])
				self.__setattr__(recordId, str(coll.insert({tableName: self.__getattr__(tableName).tolist()})))
			else: 
				raise ValueError("Unknown record with id: {0}".format(self.__getattr__(recordId)))
		else:
			self.__setattr__(tableName, np.zeros((1, numCol)))
			self.__getattr__(tableName)[0] = np.array([self.__getattr__(paramName) for paramName in paramNames])
			self.__setattr__(recordId,  str(coll.insert({tableName: self.__getattr__(tableName).tolist()})))
	
	@staticmethod	
	def test():
		fc = PropertyCalculatorCoolprop()
		fc.fluidName = 'ParaHydrogen'
		fc.stateVariable1 = 'P'
		fc.p1 = 700e5
		fc.stateVariable2 = 'T'
		fc.T2 = 288
		fc.compute()
		print
		print fc.rho

class FluidInfo(NumericalModel):
	label = "Fluid Info"
#	figure = ModelFigure(src="ThermoFluids/img/StateDiagram3D.svg", height=150, width=250)
	description = ModelDescription('Critical point, triple point, fluid limits, other fluid constants, data sources.')
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/CoolPropLogo.png", width=150)
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
	infoInput = FieldGroup([fluidName], label = 'Fluid')
	inputs = SuperGroup([infoInput])
	
	# Actions
	computeAction = ServerAction("compute", label = "Go", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = False)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	crit_p = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
	crit_T = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
	crit_rho = Quantity('Density', default = (1, 'kg/m**3'), label = 'density')
	critPoint = FieldGroup([crit_p, crit_T, crit_rho], label = 'Critical point')

	tripple_p = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
	tripple_T = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
	tripple_rhoV = Quantity('Density', default = (1, 'kg/m**3'), label = 'vapor density')
	tripple_rhoL = Quantity('Density', default = (1, 'kg/m**3'), label = 'liquid density')
	tripplePoint = FieldGroup([tripple_p, tripple_T, tripple_rhoL, tripple_rhoV], label = 'Tripple point')
	
	t_max = Quantity('Temperature', default = (300, 'K'), label = 'Max. temperature')
	rho_max = Quantity('Density', label = 'Max. density')
	t_min = Quantity('Temperature', default = (300, 'K'), label = 'Min. temperature')
	p_max = Quantity('Pressure', default = (1, 'bar'), label = 'Max. pressure')
	fluidLimits = FieldGroup([t_max, rho_max, t_min, p_max], label = 'Fluid limits')
	
	molar_mass = Quantity('MolarMass', label = 'molar mass')
	accentric_factor = Quantity('Dimensionless', label = 'accentric factor')
	cas = String('CAS', label = 'CAS')
	ashrae34 = String('ASHRAE34', label = 'ASHRAE34')
	references = String(show="false")
	
	other = FieldGroup([references, molar_mass, accentric_factor, cas, ashrae34], label = 'Other')
	results = SuperGroup([critPoint, tripplePoint, fluidLimits, other])
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	# Html section
	litRefs = HtmlBlock(srcType="file", src="FluidInfoLitReferences.jinja")
	
	############# Page structure ########
	modelBlocks = [inputView, resultView, litRefs]
	
	############# Methods ###############	
	def compute(self):
		f = Fluid(self.fluidName)
		crit = f.critical
		self.crit_p = crit['p']
		self.crit_T = crit['T']
		self.crit_rho = crit['rho']

		tripple = f.tripple
		self.tripple_p = tripple['p']
		self.tripple_T = tripple['T']
		self.tripple_rhoV = tripple['rhoV']
		self.tripple_rhoL = tripple['rhoL']
		
		fLimits = f.fluidLimits
		self.t_max = fLimits['TMax']
		self.rho_max = fLimits['rhoMax']
		self.t_min = fLimits['TMin']
		self.p_max = fLimits['pMax']
		
		self.molar_mass = f.molarMass*1e-3
		self.accentric_factor = f.accentricFactor
		self.cas = f.CAS
		self.ashrae34 = f.ASHRAE34
		self.references = self.getReferences()

	def getReferences(self):
		f = Fluid(self.fluidName)
		refList = []
		for key in referenceKeys:
			try:
				reference = References[f.BibTeXKey(key)]
			except KeyError:
				reference = None
			refList.append([referenceKeys[key], reference])
		return refList

class SaturationData(NumericalModel):
	label = "Saturation Data"
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/CoolPropLogo.png", width=150)
	description = ModelDescription('Evaporation and condensation data')
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid', description="Fluid to select to calculate saturation data. Fluid to select to calculate saturation data. Fluid to select to calculate saturation data. Fluid to select to calculate saturation data. Fluid to select to calculate saturation data. Fluid to select to calculate saturation data. ")
	satInput = FieldGroup([fluidName], label = 'Fluid')
	inputs = SuperGroup([satInput])
	
	# Actions
	computeAction = ServerAction("compute", label = "Go", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = False)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	############# Results ###############
	# Fields
	T_p_satPlot = PlotView(label = 'Temperature', dataLabels = ['pressure [Pa]', 'saturation temperature [K]'], 
							xlog = True, 
							options = {'ylabel': 'temperature [K]'}, description="Temperature pressure saturation plot")
	rho_p_satPlot = PlotView(label = 'Density', dataLabels = ['pressure [Pa]', 'liquid density [kg/m**3]', 'vapor density [kg/m**3]'],
							options = {'ylabel': 'density [kg/m**3]'})
	delta_h_p_satPlot = PlotView(label = 'Evap. enthalpy', dataLabels = ['pressure [Pa]', 'h evap [kJ/kg]'], 
								xlog = True, 
								options = {'title': 'Evaporation enthalpy'}, description="Evaporation enthalpy pressure saturation")
	delta_s_p_satPlot = PlotView(label = 'Evap. entropy', dataLabels = ['pressure [Pa]', 's evap. [kJ/kg-K]'],
								xlog = True,  
								options = {'title': 'Evaporation entropy'})
	
	satTableView = TableView(label = 'Sat. table', dataLabels = ['p', 'T', 'rho_L', 'rho_V', 'h_L', 
											'h_V', 'h_V - h_L', 's_L', 's_V', 
											's_V - s_L'],
									quantities = ['Pressure', 'Temperature', 'Density', 'Density', 'SpecificEnthalpy',
												'SpecificEnthalpy', 'SpecificEnthalpy', 'SpecificEntropy', 'SpecificEntropy',
												'SpecificEntropy'], 
									options = {'title': 'Saturation data', 'formats': '0.0000E0'})
	
	satViewGroup = ViewGroup([T_p_satPlot, rho_p_satPlot, delta_h_p_satPlot, delta_s_p_satPlot,
								satTableView], label="Saturation Data")
	results = SuperGroup([satViewGroup])
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	############# Methods ###############	
	def compute(self):
		f = Fluid(self.fluidName)
		fState = FluidState(self.fluidName)
		numPoints = 100
		pressures = np.logspace(np.log10(f.tripple['p']), np.log10(f.critical['p']), numPoints, endpoint = False)
		data = np.zeros((numPoints, 10))
		data[:,0] = pressures
		
		for i in range(len(pressures)):
			fState.update_pq(pressures[i], 0)			
			satL = fState.SatL
			satV = fState.SatV
			
			data[i,1] = fState.T
			data[i,2] = satL.rho
			data[i,3] = satV.rho
			data[i,4] = satL.h
			data[i,5] = satV.h
			data[i,7] = satL.s
			data[i,8] = satV.s
		# Compute evaporation enthalpy
		data[:,6] = data[:, 5] - data[:, 4]	
		# Compute evaporation entropy
		data[:,9] = data[:, 8] - data[:, 7]	

		self.T_p_satPlot = data[:,(0,1)]		
		self.rho_p_satPlot = data[:, (0, 2, 3)]
		self.delta_h_p_satPlot = data[:, (0, 6)]	
		self.delta_s_p_satPlot = data[:, (0, 9)]
		self.satTableView = data

class PHDiagramModel(NumericalModel):
	label = 'P-H Diagram'
	figure = ModelFigure(src="ThermoFluids/img/ModuleImages/water_PHDiagram.png", width=200, show = False)
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(PHDiagramFluids, default = 'ParaHydrogen', label = 'fluid')
	isotherms = Boolean(label = 'isotherms')
	isochores = Boolean(label = 'isochores')
	isentrops = Boolean(label = 'isentrops')
	qIsolines = Boolean(label = 'vapor quality isolines')
	
	infoInput = FieldGroup([fluidName, isotherms, isochores, isentrops, qIsolines], 
							label = 'Diagram Inputs')
	inputs = SuperGroup([infoInput])
	
	# Actions
	computeAction = ServerAction("compute", label = "Go", outputView = 'resultView')
	inputActionBar = ActionBar([computeAction], save = False)
	
	# Model view
	inputView = ModelView(ioType = "input", superGroups = [inputs], 
		actionBar = inputActionBar, autoFetch = True)
	
	diagram = Image(default='', width=880, height=550)
	diagramViewGroup = ViewGroup([diagram], label = "P-H Diagram")
	results = SuperGroup([diagramViewGroup])
	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [results])
	
	############# Page structure ########
	modelBlocks = [inputView, resultView]
	
	def compute(self):
		diagram = PHDiagram(self.fluidName)
		diagram.setLimits()
		fHandle, resourcePath  = diagram.draw(isotherms=self.isotherms, 
												isochores=self.isochores, 
												isentrops=self.isentrops, 
												qIsolines=self.qIsolines)
		self.diagram = resourcePath
		os.close(fHandle)
		
class FluidPropertiesDoc(RestModule):
	name = 'FluidPropertiesDoc'
	label = 'Fluid Properties (Docs)'
		
if __name__ == '__main__':
# 	PropertyCalculatorCoolprop.test()
# 	print getFluidConstants()
# 	print getLiteratureReferences()
	FluidInfo.test()
