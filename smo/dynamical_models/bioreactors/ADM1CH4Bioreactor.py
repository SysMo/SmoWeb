'''
Created on Mar 08, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import pylab as plt
import Constnat as Const

from smo.util import AttributeDict 
from assimulo.exception import TerminateSimulation
from smo.dynamical_models.core.Simulation import Simulation, TimeEvent, ResultStorage
from smo.math.util import NamedStateVector

""" Global Settings """
import os
from SmoWeb.settings import MEDIA_ROOT
tmpFolderPath = os.path.join (MEDIA_ROOT, 'tmp')
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_ADM1CH4Bioreactor_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/ADM1CH4Bioreactor'

class ADM1TimeEvent(TimeEvent):	
	"""
	Class for time event of ADM1 models
	"""
	def __init__(self, t, newValue_D):
		self.t = t
		self.newValue_D = newValue_D
		
		self.eventType = "ADM1_TIME_EVENT"
		self.description = "Change the dilution rate (D) to {0}".format(newValue_D)
		
class ADM1CH4Bioreactor(Simulation):
	"""
	Class for implementation the model of a ADM1 CH4Bioreactor
	"""
	name = 'Model of a bioreactor that produces hydrogen.'
	
	def __init__(self, webModel, params, concentrs, **kwargs):
		super(ADM1CH4Bioreactor, self).__init__(**kwargs)
		
		# Initialize update progress function
		self.updateProgress = webModel.updateProgress
					
		# Initialize parameters		
		self.params = params
		self.K_H_ch4 = 0.0014 * np.exp(
			-14240./(Const.R*100.) * (1/params.T_base - 1/params.T_op))
		
		self.D_gas = params.q_gas/params.V_gas
		#:TRICKY: compute D values using D = q/V
		self.D_liq_vals = np.copy(params.q_liq_vals)
		for D_liq in self.D_liq_vals:
			q_liq = D_liq[1]
			D_liq[1] = q_liq / params.V_liq
			
		# Initialize concentrations
		self.concentrs = concentrs
		
		# Create state vector and derivative vector
		stateVarNames = [
			'S_ac', 'S_ch4',
			'X_ac',  
			'S_gas_ch4', 'm_gas_ch4',
		] 
		self.y = NamedStateVector(stateVarNames)
		self.yRes = NamedStateVector(stateVarNames)
		self.yDot = NamedStateVector(stateVarNames)

		# Initialize data storage
		self.resultStorage = ResultStorage(
			filePath = dataStorageFilePath,
			datasetPath = dataStorageDatasetPath)
		if (kwargs.get('initDataStorage', True)):
			self.resultStorage.initializeWriting(
				varList = ['t'] + stateVarNames + ['D'],
				chunkSize = 1e4)
		
		# Register time event (changed of D)
		D_liq = self.D_liq_vals[0]
		self.D = D_liq[1]
		tChangedD = D_liq[0]
		
		for i in range(len(self.D_liq_vals)-1):
			D_liq = self.D_liq_vals[i+1]
			self.timeEventRegistry.add(ADM1TimeEvent(t = tChangedD, newValue_D = D_liq[1]))
			tChangedD += D_liq[0]
		
		# Set initial values of the states
		self.y.S_ac = concentrs.S_ac_0
		self.y.S_ch4 = concentrs.S_ch4_0
		self.y.X_ac = concentrs.X_ac_0
		self.y.S_gas_ch4 = concentrs.S_gas_ch4_0
		self.y.m_gas_ch4 = 0.0		
				
		# Set all the initial state values
		self.y0 = self.y.get(copy = True)
		
		# Set the initial flags
		self.sw0 = [True]
		
	def rhs(self, t, y, sw):
		params = self.params
		concentrs = self.concentrs
		
		# Set state values
		self.y.set(y)
		
		try:
			# Get state values
			S_ac = self.y.S_ac
			S_ch4 = self.y.S_ch4
			X_ac = self.y.X_ac
			S_gas_ch4 = self.y.S_gas_ch4
			
			# Compute biochemical process rates
			r11 = params.k_m_ac * (S_ac / (params.K_S_ac + S_ac)) * X_ac
			
			# Compute transfer rates
			p_gas_ch4 = S_gas_ch4 * (Const.R * params.T_op)/64.
			r_T_9 = params.kLa_ch4 * (S_ch4 - 64 * self.K_H_ch4 * p_gas_ch4)
			
			# Compute state derivatives		
			S_ac_dot = self.D*(concentrs.S_ac_in - S_ac) -r11#7.2
			S_ch4_dot = self.D*(concentrs.S_ch4_in - S_ch4) + \
				(1-params.Y_ac)*r11 - r_T_9 #9.2
			X_ac_dot = self.D*(concentrs.X_ac_in - X_ac) + params.Y_ac * r11 #22.2
			S_gas_ch4_dot = self.D_gas*(0. - S_gas_ch4) + r_T_9 * params.V_liq / params.V_gas #1.2
			m_gas_ch4_dot = params.q_gas * S_gas_ch4
			
		except Exception, e:
			self.resultStorage.finalizeResult()
			# Log the error if it happens in the rhs() function
			print("Exception at time {}: {}".format(t, e))
			raise e
			
		self.yDot.S_ac = S_ac_dot
		self.yDot.S_ch4 = S_ch4_dot
		self.yDot.X_ac = X_ac_dot
		self.yDot.S_gas_ch4 = S_gas_ch4_dot
		self.yDot.m_gas_ch4 = m_gas_ch4_dot
		return self.yDot.get()
	
	
	def state_events(self, t, y, sw):
		eventIndicators = np.ones(len(sw))
		return eventIndicators
	
	def step_events(self, solver):
		# Called on each time step
		pass
	
	def handle_event(self, solver, eventInfo):
		reportEvents = True
		_stateEventInfo, timeEvent = eventInfo
		
		# Handle time events
		if (timeEvent):
			timeEventList = self.processTimeEvent(solver.t)
			self.D = timeEventList[0].newValue_D
			if (reportEvents):
				print("Time event located at time: {} - {}".format(solver.t, timeEventList[0].description))
	
		if (False):
			raise TerminateSimulation()
	
	def handle_result(self, solver, t, y):
		super(ADM1CH4Bioreactor, self).handle_result(solver, t, y)
		self.updateProgress(t, self.tFinal)
			
		self.yRes.set(y)
		self.resultStorage.record[:] = (t, 
			self.yRes.S_ac, self.yRes.S_ch4,  
			self.yRes.X_ac, 
			self.yRes.S_gas_ch4, self.yRes.m_gas_ch4,
			self.D,
		)
		self.resultStorage.saveTimeStep()
	
	def plotHDFResults(self):		
		# Load the results
		self.resultStorage.openStorage()
		data = self.resultStorage.loadResult()
		
		# Set the results
		xData = data['t']
		plt.plot(xData, data['S_ac'], 'r', label = 'S_ac')
		plt.plot(xData, data['S_ch4'], 'b', label = 'S_ch4')
		plt.plot(xData, data['X_ac'], 'g', label = 'X_ac')
		plt.plot(xData, data['S_gas_ch4'], 'g--', label = 'S_gas_ch4')
		plt.plot(xData, data['D'], 'm', label = 'D')
		
		# Close the result storage
		self.resultStorage.closeStorage()
		
		# Plot the results
		plt.gca().set_xlim([0, xData[-1]])
		plt.legend()
		plt.show()


def TestADM1CH4Bioreactor():
	print "=== BEGIN: TestADM1CH4Bioreactor ==="
	
	# Settings
	simulate = True #True - run simulation; False - plot an old results 
	
	# Initialize simulation parameters
	solverParams = AttributeDict({
		'tFinal' : 10., 
		'tPrint' : .1,
	})
		
	# Initialize model parameters
	# Validation of prameters
	#f_ch_xc + f_pr_xc + f_li_xc + [f_xI_xc + f_sI_xc] = 1.0
	#[f_bu_su + f_pro_su] + f_ac_su + f_h2_su = 1.0
	#[f_va_aa + f_bu_aa + f_pro_aa] + f_ac_aa + f_h2_aa = 1.0
	#Y_xx < = 1.0
	class ModelParams:
		#Stoichiometric parameter values
		Y_ac = 0.05 #-
		
		#Biochemical parameter values
		k_m_ac = 8.0 #1/day
		K_S_ac = 0.15 #kgCOD/m**3
		
		# Physiochemical parameter values
		T_base = 298.15 #K
		T_op = 308.15 #K
	
		kLa_ch4 = 200 #1/day
		
		# Physical parameters
		V_liq = 3.4 #L
		V_gas = 0.3 #L
		
		# Controller - D = q/V
		q_liq_vals = np.array([[100, 0.17], ]) #[day, L/day] (liquid)
		q_gas = 3.0 #L/day
	modelParams = ModelParams()		
		
	class ModelConcentrs:
		# Input concentrations 
		S_ac_in = 0.2 #kgCOD/m**3
		S_ch4_in = 1e-5 #kgCOD/m**3
		X_ac_in = 0 * 0.01 #kgCOD/m**3
		
		# Initial values of state variables 
		S_ac_0 = 0.2 #kgCOD/m**3
		S_ch4_0 = 0.055 #kgCOD/m**3
		X_ac_0 = 0.76 #kgCOD/m**3
		S_gas_ch4_0 = 1e-5 #kgCOD/m**3
	modelConcentrs = ModelConcentrs()

	webModel = AttributeDict({
		'updateProgress' : lambda x, y : x, #:TRICKY: not used,
	})
		
	# Create the model
	bioreactor = ADM1CH4Bioreactor(webModel = webModel, params = modelParams, concentrs = modelConcentrs, initDataStorage = simulate)
	
	# Run simulation or load old results
	if (simulate == True):
		bioreactor.prepareSimulation()
		bioreactor.run(solverParams)
	else:
		bioreactor.loadResult(simIndex = 1)
	
	# Export to csv file
	bioreactor.resultStorage.exportToCsv(fileName = csvFileName)
	
	# Plot results
	bioreactor.plotHDFResults()
	
	print "=== END: TestADM1CH4Bioreactor ==="
	
	
if __name__ == '__main__':
	TestADM1CH4Bioreactor()