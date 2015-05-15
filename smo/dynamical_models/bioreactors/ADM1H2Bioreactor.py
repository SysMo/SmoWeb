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
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_ADM1H2Bioreactor_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/ADM1H2Bioreactor'

class ADM1TimeEvent(TimeEvent):	
	"""
	Class for time event of ADM1 models
	"""
	def __init__(self, t, newValue_D):
		self.t = t
		self.newValue_D = newValue_D
		
		self.eventType = "ADM1_TIME_EVENT"
		self.description = "Change the dilution rate (D) to {0}".format(newValue_D)
		
class ADM1H2Bioreactor(Simulation):
	"""
	Class for implementation the model of a ADM1 H2Bioreactor
	"""
	name = 'Model of a bioreactor that produces hydrogen.'
	
	def __init__(self, webModel, params, concentrs, **kwargs):
		super(ADM1H2Bioreactor, self).__init__(**kwargs)
		
		# Initialize update progress function
		self.updateProgress = webModel.updateProgress
					
		# Initialize parameters		
		self.params = params
		self.K_H_h2 = 7.8e-4 * np.exp(
			-4180./(Const.R*100.) * (1/params.T_base - 1/params.T_op))
				
		# Initialize concentrations
		self.concentrs = concentrs
		
		# Create state vector and derivative vector
		stateVarNames = [
			'S_su', 'S_aa', 'S_fa', 'S_ac', 'S_h2',
			'X_c', 'X_ch', 'X_pr', 'X_li', 'X_su', 'X_aa', 'X_fa', 
			'S_gas_h2', 'm_gas_h2',
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
		D_liq = params.D_liq_vals[0]
		self.D = D_liq[1]
		tChangedD = D_liq[0]
		
		for i in range(len(params.D_liq_vals)-1):
			D_liq = self.D_liq_vals[i+1]
			self.timeEventRegistry.add(ADM1TimeEvent(t = tChangedD, newValue_D = D_liq[1]))
			tChangedD += D_liq[0]
		
		# Set initial values of the states
		self.y.S_su = concentrs.S_su_0
		self.y.S_aa = concentrs.S_aa_0
		self.y.S_fa = concentrs.S_fa_0
		self.y.S_ac = concentrs.S_ac_0
		self.y.S_h2 = concentrs.S_h2_0
		self.y.X_c = concentrs.X_c_0
		self.y.X_ch = concentrs.X_ch_0
		self.y.X_pr = concentrs.X_pr_0
		self.y.X_li = concentrs.X_li_0
		self.y.X_su = concentrs.X_su_0
		self.y.X_aa = concentrs.X_aa_0
		self.y.X_fa = concentrs.X_fa_0
		self.y.S_gas_h2 = concentrs.S_gas_h2_0
		self.y.m_gas_h2 = 0.0		
				
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
			S_su = self.y.S_su
			S_aa = self.y.S_aa
			S_fa = self.y.S_fa
			S_ac = self.y.S_ac
			S_h2 = self.y.S_h2
			X_c = self.y.X_c
			X_ch = self.y.X_ch
			X_pr = self.y.X_pr
			X_li = self.y.X_li
			X_su = self.y.X_su
			X_aa = self.y.X_aa
			X_fa = self.y.X_fa
			S_gas_h2 = self.y.S_gas_h2
			
			# Compute biochemical process rates
			r1 = params.k_dis * X_c
			r2 = params.k_hyd_ch * X_ch
			r3 = params.k_hyd_pr * X_pr
			r4 = params.k_hyd_li * X_li
			r5 = params.k_m_su * (S_su / (params.K_S_su + S_su)) * X_su
			r6 = params.k_m_aa * (S_aa / (params.K_S_aa + S_aa)) * X_aa
			r7 = params.k_m_fa * (S_fa / (params.K_S_fa + S_fa)) * X_fa
			
			# Compute transfer rates
			p_gas_h2 = S_gas_h2 * (Const.R * params.T_op)/16.
			r_T_8 = params.kLa_h2 * (S_h2 - 16 * self.K_H_h2 * p_gas_h2)
			
			# Compute state derivatives		
			S_su_dot = self.D*(concentrs.S_su_in - S_su) + r2 + (1 - params.f_fa_li)*r4 - r5 #1.1
			S_aa_dot = self.D*(concentrs.S_aa_in - S_aa) + r3 - r6 #2.1
			S_fa_dot = self.D*(concentrs.S_fa_in - S_fa) + params.f_fa_li*r4 - r7 #3.1
			S_ac_dot = self.D*(concentrs.S_ac_in - S_ac) + (1 - params.Y_su)*params.f_ac_su*r5 \
				+ (1 - params.Y_aa)*params.f_ac_aa*r6 \
				+ (1 - params.Y_fa)*0.7*r7 #7.1
			S_h2_dot = self.D*(concentrs.S_h2_in - S_h2) + (1 - params.Y_su)*params.f_h2_su*r5 \
				+ (1 - params.Y_aa)*params.f_h2_aa*r6 \
				+ (1 - params.Y_fa)*0.3*r7 \
				- r_T_8 #8.1
			X_c_dot = self.D*(concentrs.X_c_in - X_c) - r1 #13.1
			X_ch_dot = self.D*(concentrs.X_ch_in - X_ch) + params.f_ch_xc*r1 - r2 #14.1
			X_pr_dot = self.D*(concentrs.X_pr_in - X_pr) + params.f_pr_xc*r1 - r3 #15.1
			X_li_dot = self.D*(concentrs.X_li_in - X_li) + params.f_li_xc*r1 - r4 #16.1
			X_su_dot = self.D*(concentrs.X_su_in - X_su) + params.Y_su*r5 #17.1
			X_aa_dot = self.D*(concentrs.X_aa_in - X_aa) + params.Y_aa*r6 #18.1
			X_fa_dot = self.D*(concentrs.X_aa_in - X_fa) + params.Y_fa*r7 #19.1
			
			S_gas_h2_dot = params.D_gas*(0. - S_gas_h2) + r_T_8 * params.V_liq_del_V_gas #1.1
			m_gas_h2_dot = params.D_gas * S_gas_h2
			
		except Exception, e:
			self.resultStorage.finalizeResult()
			# Log the error if it happens in the rhs() function
			print("Exception at time {}: {}".format(t, e))
			raise e
			
		self.yDot.S_su = S_su_dot
		self.yDot.S_aa = S_aa_dot
		self.yDot.S_fa = S_fa_dot
		self.yDot.S_ac = S_ac_dot
		self.yDot.S_h2 = S_h2_dot
		self.yDot.X_c = X_c_dot
		self.yDot.X_ch = X_ch_dot
		self.yDot.X_pr = X_pr_dot
		self.yDot.X_li = X_li_dot
		self.yDot.X_su = X_su_dot
		self.yDot.X_aa = X_aa_dot
		self.yDot.X_fa = X_fa_dot
		self.yDot.S_gas_h2 = S_gas_h2_dot
		self.yDot.m_gas_h2 = m_gas_h2_dot
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
		super(ADM1H2Bioreactor, self).handle_result(solver, t, y)
		self.updateProgress(t, self.tFinal)
			
		self.yRes.set(y)
		self.resultStorage.record[:] = (t, 
			self.yRes.S_su, self.yRes.S_aa, self.yRes.S_fa, self.yRes.S_ac, self.yRes.S_h2,  
			self.yRes.X_c, self.yRes.X_ch, self.yRes.X_pr, self.yRes.X_li, self.yRes.X_su, self.yRes.X_aa, self.yRes.X_fa,
			self.yRes.S_gas_h2, self.yRes.m_gas_h2,
			self.D,
		)
		self.resultStorage.saveTimeStep()
			
	def plotHDFResults(self):		
		# Load the results
		self.resultStorage.openStorage()
		data = self.resultStorage.loadResult()
		
		# Set the results
		xData = data['t']
		plt.plot(xData, data['S_su'], 'r', label = 'S_su')
		plt.plot(xData, data['S_aa'], 'b', label = 'S_aa')
		plt.plot(xData, data['S_h2'], 'g', label = 'S_h2')
		plt.plot(xData, data['S_gas_h2'], 'g--', label = 'S_gas_h2')
		plt.plot(xData, data['m_gas_h2'], 'm--', label = 'm_gas_h2 [kg/m**3]')
		plt.plot(xData, data['D'], 'm', label = 'D')
		
		# Close the result storage
		self.resultStorage.closeStorage()
		
		# Plot the results
		plt.gca().set_xlim([0, xData[-1]])
		plt.legend()
		plt.show()


def TestADM1H2Bioreactor():
	print "=== BEGIN: TestADM1H2Bioreactor ==="
	
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
		f_ch_xc = 0.2 #-
		f_pr_xc = 0.2 #-
		f_li_xc = 0.3 #-
		
		f_fa_li = 0.95 #-
		
		f_ac_su = 0.41 #-
		f_h2_su = 0.19 #-
		
		f_ac_aa = 0.4 #-
		f_h2_aa = 0.06 #-
		
		Y_su = 0.1 #-
		Y_aa = 0.08 #-
		Y_fa = 0.06 #-
		
		#Biochemical parameter values
		k_dis = 0.5 #1/day
		
		k_hyd_ch = 10.0 #1/day
		k_hyd_pr = 10.0 #1/day
		k_hyd_li = 10.0 #1/day
		
		k_m_su = 30.0 #1/day
		K_S_su = 0.5 #g/L
		
		k_m_aa = 50.0 #1/day
		K_S_aa = 0.3 #g/L 
		
		k_m_fa = 6.0 #1/day
		K_S_fa = 0.4 #g/L
		
		# Physiochemical parameter values
		T_base = 298.15 #K
		T_op = 308.15 #K
	
		kLa_h2 = 200 #1/day
		
		# Physical parameters
		V_liq_del_V_gas = 3.0 #L/L 
		
		# Controller - D = q/V
		D_liq_vals = np.array([[100, 1], ]) #[day, 1/day] (liquid)
		D_gas = 3.0 #1/day
	modelParams = ModelParams()		
		
	class ModelConcentrs:
		# Input concentrations 
		S_su_in = 0 * 0.01 #gCOD/L
		S_aa_in = 0 * 0.001 #gCOD/L
		S_fa_in = 0 * 0.001 #gCOD/L
		S_ac_in = 0 * 0.001 #gCOD/L
		S_h2_in = 0 * 1e-8 #gCOD/L
		X_c_in = 2.0 #gCOD/L
		X_ch_in = 5.0 #gCOD/L
		X_pr_in = 20.0 #gCOD/L
		X_li_in = 5.0 #gCOD/L
		X_su_in = 0 * 0.01 #g/L
		X_aa_in = 0 * 0.01 #g/L
		X_fa_in = 0 * 0.01 #g/L
		
		# Initial values of state variables 
		S_su_0 = 0.01 #gCOD/L
		S_aa_0 = 0.001 #gCOD/L
		S_fa_0 = 0.001 #gCOD/L
		S_ac_0 = 0.001 #gCOD/L
		S_h2_0 = 1e-8 #gCOD/L
		X_c_0 = 2.0 #gCOD/L
		X_ch_0 = 5.0 #gCOD/L
		X_pr_0 = 20.0 #gCOD/L
		X_li_0 = 5.0 #gCOD/L
		X_su_0 = 0.01 #g/L
		X_aa_0 = 0.01 #g/L
		X_fa_0 = 0.01 #g/L
		S_gas_h2_0 = 1e-5 #gCOD/L
	modelConcentrs = ModelConcentrs()
	
	webModel = AttributeDict({
		'updateProgress' : lambda x, y : x, #:TRICKY: not used,
	})
	
	
	# Create the model
	bioreactor = ADM1H2Bioreactor(webModel = webModel, params = modelParams, concentrs = modelConcentrs, initDataStorage = simulate)
	
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
	
	print "=== END: TestADM1H2Bioreactor ==="
	
	
if __name__ == '__main__':
	TestADM1H2Bioreactor()