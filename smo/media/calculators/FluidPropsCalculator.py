'''
Created on Nov 05, 2014
@author: Atanas Pavlov
'''
import numpy as np
from collections import OrderedDict
from smo.model.model import NumericalModel, ModelView, ModelDocumentation, HtmlBlock
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.CoolProp.CoolProp import Fluid, FluidState
from smo.media.MaterialData import Fluids
from smo.media.CoolProp.CoolPropReferences import References

from pymongo import MongoClient
from bson.objectid import ObjectId
mongoClient = MongoClient()

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

class FluidProperties(NumericalModel):
	name = "FluidProperties"
	label = "Fluid Properties"
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')	
	stateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
	p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable1 == 'P'")
	T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
	rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
	h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
	s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable1 == 'S'")
	q1 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable1 == 'Q'")
	stateVariable2 = Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
	p2 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
	T2 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
	rho2 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
	h2 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
	s2 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable2 == 'S'")
	q2 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable2 == 'Q'")
	####
	stateGroup1 = FieldGroup([fluidName], label = 'Fluid')
	stateGroup2 = FieldGroup([stateVariable1, p1, T1, rho1, h1, s1, q1, stateVariable2, p2, T2, rho2, h2, s2, q2], label = 'States')
	inputs = SuperGroup([stateGroup1, stateGroup2])
	
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
	dpdt_v = Quantity('Dimensionless', label = '(dp/dT)<sub>v</sub>')
	dpdv_t = Quantity('Dimensionless', label = '(dp/dv)<sub>T</sub>')
	#####
	stateVariablesResults = FieldGroup([recordId, T, p, rho, h, s, q, u], label = 'States')
	derivativeResults = FieldGroup([cp, cv, gamma, Pr, cond, mu, dpdt_v, dpdv_t], label = 'Derivatives & Transport')
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
	paramVarTable = TableView(label="Variation Table", dataLabels = ['T[K]', 'p[Pa]', 'h[J/kg]'], 
							visibleColumns = [1,2], options = {'formats': ['0.0000E0', '0.000', '0.000']})
	paramVariation = ViewGroup([paramVarTable], label="Parameter Variation")
	FluidPoints = SuperGroup([paramVariation], label = "Fluid Points")	
	# Model view
	resultView = ModelView(ioType = "output", superGroups = [props, FluidPoints])
	resultViewIsTwoPhase = ModelView(ioType = "output", superGroups = [props, saturationProps, FluidPoints])
	
	# Html section
	imgSection = HtmlBlock(srcType="string", 
							src='<div class="title-figure">\
									<img height="150" style="width: 250px" src="{static}/ThermoFluids/StateDiagram3D.svg/"></img>\
								</div>')
	
	############# Page structure ########
	modelBlocks = [imgSection, inputView, resultView, resultViewIsTwoPhase]

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
		self.dpdt_v = fState.dpdt_v
		self.dpdv_t = fState.dpdv_t
		
		self.isTwoPhase = fState.isTwoPhase()
		if (self.isTwoPhase == True):
			satL = fState.getSatL()			
			satV = fState.getSatV()
			
			self.rho_L = satL['rho']
			self.h_L = satL['h']/1e3
			self.s_L = satL['s']/1e3
			
			self.rho_V = satV['rho']
			self.h_V = satV['h']/1e3
			self.s_V = satV['s']/1e3
				
		self.computeParamVarTable('paramVarTable', 'recordId', ['T', 'p', 'h'])
		
	def computeParamVarTable(self, tableName, recordId, paramNames):
		db = mongoClient.SmoWeb
		coll = db[self.__class__.__name__ + '_' + tableName]
		numCol = len(paramNames)
		if (self.__dict__[recordId] != ''):			
			record = coll.find_one({"_id": ObjectId(self.__dict__[recordId])})
			if (record is not None):
				recordValues = record[tableName]
				numRows = len(recordValues)
				self.__dict__[tableName] = np.zeros((numRows + 1, numCol))
				self.__dict__[tableName][0:numRows] = np.array(recordValues)
				self.__dict__[tableName][numRows] = np.array([self.__dict__[paramName] for paramName in paramNames])
				self.__dict__[recordId] = str(coll.insert({tableName: self.__dict__[tableName].tolist()}))
			else: 
				raise ValueError("Unknown record with id: {0}".format(self.__dict__[recordId]))
		else:
			self.__dict__[tableName] = np.zeros((1, numCol))
			print [self.__dict__[paramName] for paramName in paramNames]
			self.__dict__[tableName][0] = np.array([self.__dict__[paramName] for paramName in paramNames])
			self.__dict__[recordId] = str(coll.insert({tableName: self.__dict__[tableName].tolist()}))
	
	@staticmethod	
	def test():
		fc = FluidProperties()
		fc.fluidName = 'ParaHydrogen'
		fc.stateVariable1 = 'P'
		fc.p1 = 700e5
		fc.stateVariable2 = 'T'
		fc.T2 = 288
		fc.compute()
		print
		print fc.rho
		

class FluidInfo(NumericalModel):
	name = "FluidInfo"
	label = "Fluid Info"
	
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
	litRefs = HtmlBlock(srcType="file", src="FluidInfoLitReferences.html")
	
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
		
		self.molar_mass = f.molarMass*10**-3
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
	name = "SaturationData"
	label = "Saturation Data"
	
	############# Inputs ###############
	# Fields
	fluidName = Choices(Fluids, default = 'ParaHydrogen', label = 'fluid')
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
	T_p_satPlot = PlotView(label = 'Temperature', dataLabels = ['pressure [bar]', 'saturation temperature [K]'], 
							xlog = True, 
							options = {'ylabel': 'temperature [K]'})
	rho_p_satPlot = PlotView(label = 'Density', dataLabels = ['pressure [bar]', 'liquid density [kg/m**3]', 'vapor density [kg/m**3]'],
							options = {'ylabel': 'density [kg/m**3]'})
	delta_h_p_satPlot = PlotView(label = 'Evap. enthalpy', dataLabels = ['pressure [bar]', 'h evap [kJ/kg]'], 
								xlog = True, 
								options = {'title': 'Evaporation enthalpy'})
	delta_s_p_satPlot = PlotView(label = 'Evap. entropy', dataLabels = ['pressure [bar]', 's evap. [kJ/kg-K]'],
								xlog = True,  
								options = {'title': 'Evaporation entropy'})
	
	satTableView = TableView(label = 'Sat. table', dataLabels = ['p [bar]', 'T [K]', 'rho_L [kg/m**3]', 'rho_V [kg/m**3]', 'h_L [kJ/kg]', 
											'h_V [kJ/kg]', 'h_V - h_L [kJ/kg]', 's_L [kJ/kg-K]', 's_V [kJ/kg-K]', 
											's_V - s_L [kJ/kg-K]'], 
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
		pressures = np.logspace(np.log10(f.tripple['p']), np.log10(f.critical['p']), numPoints, endpoint = False)/1e5
		data = np.zeros((numPoints, 10))
		data[:,0] = pressures
		
		for i in range(len(pressures)):
			fState.update_pq(pressures[i]*1e5, 0)			
			satL = fState.getSatL()			
			satV = fState.getSatV()
			
			data[i,1] = fState.T
			data[i,2] = satL['rho']
			data[i,3] = satV['rho']
			data[i,4] = satL['h']/1e3
			data[i,5] = satV['h']/1e3
			data[i,7] = satL['s']/1e3
			data[i,8] = satV['s']/1e3
		# Compute evaporation enthalpy
		data[:,6] = data[:, 5] - data[:, 4]	
		# Compute evaporation entropy
		data[:,9] = data[:, 8] - data[:, 7]	

		self.T_p_satPlot = data[:,(0,1)]		
		self.rho_p_satPlot = data[:, (0, 2, 3)]
		self.delta_h_p_satPlot = data[:, (0, 6)]	
		self.delta_s_p_satPlot = data[:, (0, 9)]
		self.satTableView = data

class FluidPropertiesDoc(ModelDocumentation):
	name = 'FluidPropertiesDoc'
	label = 'Fluid Properties (Docs)'
	template = 'documentation/html/FluidPropertiesDoc.html'
		
if __name__ == '__main__':
# 	FluidProperties.test()
# 	print getFluidConstants()
# 	print getLiteratureReferences()
	FluidInfo.test()
