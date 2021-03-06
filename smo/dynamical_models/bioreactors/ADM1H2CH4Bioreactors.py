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
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_ADM1H2CH4Bioreactor_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/ADM1H2CH4Bioreactors'

class ADM1TimeEvent(TimeEvent):	
	"""
	Class for time event of ADM1 models
	"""
	def __init__(self, t, newValue_D):
		self.t = t
		self.newValue_D = newValue_D
		
		self.eventType = "ADM1_TIME_EVENT"
		self.description = "Change the dilution rate (D) to {0}".format(newValue_D)
		
class ADM1H2CH4Bioreactors(Simulation):
	"""
	Class for implementation the model of a ADM1 H2 and CH4 Bioreactors
	"""
	name = 'Model of a bioreactor that produces hydrogen.'
	
	def __init__(self, webModel, 
				paramsRH2, concentrsRH2, 
				paramsRCH4, concentrsRCH4,
				**kwargs):
		super(ADM1H2CH4Bioreactors, self).__init__(**kwargs)
		
		# Initialize update progress function
		self.updateProgress = webModel.updateProgress
					
		# Initialize parameters
		self.paramsRH2 = paramsRH2		
		self.paramsRCH4 = paramsRCH4	
				
		# Initialize concentrations
		self.concentrsRH2 = concentrsRH2
		self.concentrsRCH4 = concentrsRCH4
		
		# Create state vector and derivative vector
		stateVarNames = [
			'S_su_RH2', 'S_aa_RH2', 'S_fa_RH2', 'S_ac_RH2',
			'X_c_RH2', 'X_ch_RH2', 'X_pr_RH2', 'X_li_RH2', 'X_suaa_RH2', 'X_fa_RH2', 
			'intQ_h2_RH2',
			
			'S_ac_RCH4',
			'X_ac_RCH4', 
			'intQ_ch4_RCH4'
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
				varList = ['time'] + stateVarNames + ['Q_h2_RH2', 'Q_ch4_RCH4', 'D_RH2', 'D_RCH4'],
				chunkSize = 1e4
			)
		
		# Register time event (changed of D)
		tChangedD =  paramsRH2.D_liq_arr[0][0]
		self.D_RH2 =  paramsRH2.D_liq_arr[0][1]

		self.D_RCH4 = self.D_RH2 / paramsRCH4.V_liq_RCH4_del_V_liq_RH2
		
		for i in range(len(paramsRH2.D_liq_arr)-1):
			self.timeEventRegistry.add(
				ADM1TimeEvent(
					t = tChangedD,
					newValue_D = paramsRH2.D_liq_arr[i + 1][1]
				)
			)
			tChangedD += paramsRH2.D_liq_arr[i+1][0]
		
		# Set initial values of the states
		self.y.S_su_RH2 = concentrsRH2.S_su_0
		self.y.S_aa_RH2 = concentrsRH2.S_aa_0
		self.y.S_fa_RH2 = concentrsRH2.S_fa_0
		self.y.S_ac_RH2 = concentrsRH2.S_ac_0
		self.y.X_c_RH2 = concentrsRH2.X_c_0
		self.y.X_ch_RH2 = concentrsRH2.X_ch_0
		self.y.X_pr_RH2 = concentrsRH2.X_pr_0
		self.y.X_li_RH2 = concentrsRH2.X_li_0
		self.y.X_suaa_RH2 = concentrsRH2.X_suaa_0
		self.y.X_fa_RH2 = concentrsRH2.X_fa_0
		self.y.intQ_h2_RH2 = 0.0
		self.Q_h2_RH2 = 0.0
		
		self.y.S_ac_RCH4 = concentrsRCH4.S_ac_0
		self.y.X_ac_RCH4 = concentrsRCH4.X_ac_0
		self.y.intQ_ch4_RCH4 = 0.0
		self.Q_ch4_RCH4 = 0.0
				
		# Set all the initial state values
		self.y0 = self.y.get(copy = True)
		
		# Set the initial flags
		self.sw0 = [True]
		
	def rhs(self, t, y, sw):
		paramsRH2 = self.paramsRH2
		concentrsRH2 = self.concentrsRH2
	
		paramsRCH4 = self.paramsRCH4
		concentrsRCH4 = self.concentrsRCH4
		
		# Set state values
		self.y.set(y)
		
		try:
		# Bioreactor - RH2	
			# Get state values
			S_su_RH2 = self.y.S_su_RH2
			S_aa_RH2 = self.y.S_aa_RH2
			S_fa_RH2 = self.y.S_fa_RH2
			S_ac_RH2 = self.y.S_ac_RH2
			X_c_RH2 = self.y.X_c_RH2
			X_ch_RH2 = self.y.X_ch_RH2
			X_pr_RH2 = self.y.X_pr_RH2
			X_li_RH2 = self.y.X_li_RH2
			X_suaa_RH2 = self.y.X_suaa_RH2
			X_fa_RH2 = self.y.X_fa_RH2
			
			# Compute biochemical process rates
			r1 = paramsRH2.k_dis * X_c_RH2
			r2 = paramsRH2.k_hyd_ch * X_ch_RH2
			r3 = paramsRH2.k_hyd_pr * X_pr_RH2
			r4 = paramsRH2.k_hyd_li * X_li_RH2
			r5 = paramsRH2.k_m_suaa * (S_su_RH2 / (paramsRH2.K_S_suaa + S_su_RH2)) * X_suaa_RH2 * (S_su_RH2/(S_su_RH2+S_aa_RH2))
			r6 = paramsRH2.k_m_suaa * (S_aa_RH2 / (paramsRH2.K_S_suaa + S_aa_RH2)) * X_suaa_RH2 * (S_aa_RH2/(S_su_RH2+S_aa_RH2))
			r7 = paramsRH2.k_m_fa * (S_fa_RH2 / (paramsRH2.K_S_fa + S_fa_RH2)) * X_fa_RH2
			
			# Compute state derivatives		
			S_su_RH2_dot = self.D_RH2*(concentrsRH2.S_su_in - S_su_RH2) \
				+ r2 + paramsRH2.f_su_li*r4 - r5 #1.1
			S_aa_RH2_dot = self.D_RH2*(concentrsRH2.S_aa_in - S_aa_RH2) \
				+ r3 - r6 #2.1
			S_fa_RH2_dot = self.D_RH2*(concentrsRH2.S_fa_in - S_fa_RH2) \
				+ paramsRH2.f_fa_li*r4 - r7 #3.1
			S_ac_RH2_dot = self.D_RH2*(concentrsRH2.S_ac_in - S_ac_RH2) \
				+ (1 - paramsRH2.Y_suaa)*paramsRH2.f_ac_su*r5 \
				+ (1 - paramsRH2.Y_suaa)*paramsRH2.f_ac_aa*r6 \
				+ (1 - paramsRH2.Y_fa)*0.7*r7 #7.1
			X_c_RH2_dot = self.D_RH2*(concentrsRH2.X_c_in - X_c_RH2) \
				- r1 #13.1
			X_ch_RH2_dot = self.D_RH2*(concentrsRH2.X_ch_in - X_ch_RH2) \
				+ paramsRH2.f_ch_xc*r1 - r2 #14.1
			X_pr_RH2_dot = self.D_RH2*(concentrsRH2.X_pr_in - X_pr_RH2) \
				+ paramsRH2.f_pr_xc*r1 - r3 #15.1
			X_li_RH2_dot = self.D_RH2*(concentrsRH2.X_li_in - X_li_RH2) \
				+ paramsRH2.f_li_xc*r1 - r4 #16.1
			X_suaa_RH2_dot = self.D_RH2*(concentrsRH2.X_suaa_in - X_suaa_RH2) \
				+ paramsRH2.Y_suaa*r5 \
				+ paramsRH2.Y_suaa*r6 #17.1
			X_fa_RH2_dot = self.D_RH2*(concentrsRH2.X_fa_in - X_fa_RH2) \
				+ paramsRH2.Y_fa*r7 #19.1
		
			self.Q_h2_RH2 = paramsRH2.Y_h2_su * r5 \
				+ paramsRH2.Y_h2_aa * r6 \
				+ paramsRH2.Y_h2_fa * r7
			intQ_h2_RH2_dot = self.Q_h2_RH2
			
			# Set state derivatives
			self.yDot.S_su_RH2 = S_su_RH2_dot
			self.yDot.S_aa_RH2 = S_aa_RH2_dot
			self.yDot.S_fa_RH2 = S_fa_RH2_dot
			self.yDot.S_ac_RH2 = S_ac_RH2_dot
			self.yDot.X_c_RH2 = X_c_RH2_dot
			self.yDot.X_ch_RH2 = X_ch_RH2_dot
			self.yDot.X_pr_RH2 = X_pr_RH2_dot
			self.yDot.X_li_RH2 = X_li_RH2_dot
			self.yDot.X_suaa_RH2 = X_suaa_RH2_dot
			self.yDot.X_fa_RH2 = X_fa_RH2_dot
			self.yDot.intQ_h2_RH2 = intQ_h2_RH2_dot
		
		# Bioreactor - RCH4
			# Get state values
			S_ac_RCH4 = self.y.S_ac_RCH4
			X_ac_RCH4 = self.y.X_ac_RCH4
			
			# Compute biochemical process rates
			r11 = paramsRCH4.k_m_ac * (S_ac_RCH4 / (paramsRCH4.K_S_ac + S_ac_RCH4)) * X_ac_RCH4
			
			# Compute state derivatives		
			S_ac_RCH4_dot = self.D_RCH4*(S_ac_RH2 - S_ac_RCH4) \
				-r11#7.2
			X_ac_RCH4_dot = self.D_RCH4*(concentrsRCH4.X_ac_in - X_ac_RCH4) \
				+ paramsRCH4.Y_ac * r11 #22.2
			self.Q_ch4_RCH4 = paramsRCH4.Y_ch4_ac * r11 
			intQ_ch4_RCH4_dot = self.Q_ch4_RCH4
			
			# Set state derivatives
			self.yDot.S_ac_RCH4 = S_ac_RCH4_dot
			self.yDot.X_ac_RCH4 = X_ac_RCH4_dot
			self.yDot.intQ_ch4_RCH4 = intQ_ch4_RCH4_dot
			
		except Exception, e:
			self.resultStorage.finalizeResult()
			# Log the error if it happens in the rhs() function
			print("Exception at time {}: {}".format(t, e))
			raise e
		
		return self.yDot.get()
	
	
	def state_events(self, t, y, sw):
		eventIndicators = np.ones(len(sw))
		return eventIndicators
	
	def step_events(self, solver):
		# Called on each time step
		pass
	
	def handle_event(self, solver, eventInfo):
		paramsRCH4 = self.paramsRCH4
		
		reportEvents = True
		_stateEventInfo, timeEvent = eventInfo
		
		# Handle time events
		if (timeEvent):
			timeEventList = self.processTimeEvent(solver.t)
			self.D_RH2 = timeEventList[0].newValue_D
			self.D_RCH4 = self.D_RH2 / paramsRCH4.V_liq_RCH4_del_V_liq_RH2
			if (reportEvents):
				print("Time event located at time: {} - {}".format(solver.t, timeEventList[0].description))
	
		if (False):
			raise TerminateSimulation()
	
	def handle_result(self, solver, t, y):
		super(ADM1H2CH4Bioreactors, self).handle_result(solver, t, y)
		self.updateProgress(t, self.tFinal)
			
		self.yRes.set(y)
		self.resultStorage.record[:] = (t, 
			self.yRes.S_su_RH2, self.yRes.S_aa_RH2, self.yRes.S_fa_RH2, self.yRes.S_ac_RH2,
			self.yRes.X_c_RH2, self.yRes.X_ch_RH2, self.yRes.X_pr_RH2, self.yRes.X_li_RH2, self.yRes.X_suaa_RH2, self.yRes.X_fa_RH2,
			self.yRes.intQ_h2_RH2,
			
			self.yRes.S_ac_RCH4,
			self.yRes.X_ac_RCH4, 	
			self.yRes.intQ_ch4_RCH4, 
			
			self.Q_h2_RH2,
			self.Q_ch4_RCH4,
			 
			self.D_RH2, self.D_RCH4
		)
		self.resultStorage.saveTimeStep()
			
	def plotHDFResults(self):		
		# Load the results
		self.resultStorage.openStorage()
		data = self.resultStorage.loadResult()
		
		# Set the results
		xData = data['time']
		plt.plot(xData, data['S_su_RH2'], 'r', label = 'S_su_RH2')
		plt.plot(xData, data['S_aa_RH2'], 'b', label = 'S_aa_RH2')
		#plt.plot(xData, data['S_gas_h2_RH2'], 'g--', label = 'S_gas_h2_RH2')
		#plt.plot(xData, data['m_gas_h2_RH2'], 'm--', label = 'm_gas_h2_RH2 [kg/m**3]')
		plt.plot(xData, data['D_RH2'], 'm', label = 'D_RH2')
		plt.plot(xData, data['D_RCH4'], 'm--', label = 'D_RCH4')
		
		# Close the result storage
		self.resultStorage.closeStorage()
		
		# Plot the results
		plt.gca().set_xlim([0, xData[-1]])
		plt.legend()
		plt.show()


def TestADM1H2CH4Bioreactor():
	print "=== BEGIN: TestADM1H2CH4Bioreactor ==="
	
	# Settings
	simulate = True #True - run simulation; False - plot an old results 
	
	# Initialize simulation parameters
	solverParams = AttributeDict({
		'tFinal' : 50., 
		'tPrint' : .1,
		'absTol' : 1e-9,
		'relTol' : 1e-7,
	})
		
	# Initialize model parameters

	# Validation of prameters
	#f_su_li + f_fa_li <= 1.0
	#f_ch_xc + f_pr_xc + f_li_xc + [f_xI_xc + f_sI_xc] = 1.0
	#[f_bu_su + f_pro_su] + f_ac_su + f_h2_su = 1.0
	#[f_va_aa + f_bu_aa + f_pro_aa] + f_ac_aa + f_h2_aa = 1.0
	#Y_xx < = 1.0
	class ModelParamsRH2:
		#Stoichiometric parameter values
		f_ch_xc = 0.2 #-
		f_pr_xc = 0.2 #-
		f_li_xc = 0.3 #-
		
		f_su_li = 0.05 #-
		f_fa_li = 0.90 #-
		
		f_ac_su = 0.41 #-
		
		f_ac_aa = 0.4 #-
		
		Y_suaa = 0.1 #-
		Y_fa = 0.06 #-
		
		
		#Biochemical parameter values
		k_dis = 0.5 #1/day
		
		k_hyd_ch = 10.0 #1/day
		k_hyd_pr = 10.0 #1/day
		k_hyd_li = 10.0 #1/day
		
		k_m_suaa = 30.0 #1/day
		K_S_suaa = 0.5 #g/L
		
		k_m_fa = 6.0 #1/day
		K_S_fa = 0.4 #g/L
	
		#kLa_h2 = 200 #1/day
		Y_h2_su = 1.0 #-
		Y_h2_aa = 1.0 #-
		Y_h2_fa = 1.0 #-
		
		# Controller - D = q/V
		D_liq_arr = np.array([[10., 1.], [20.,2.]]) #[day, 1/day] (liquid)
	modelParamsRH2 = ModelParamsRH2()		
		
	class ModelConcentrsRH2:
		# Input concentrations 
		S_su_in = 0 * 0.01 #gCOD/L
		S_aa_in = 0 * 0.001 #gCOD/L
		S_fa_in = 0 * 0.001 #gCOD/L
		S_ac_in = 0 * 0.001 #gCOD/L
		X_c_in = 2.0 #gCOD/L
		X_ch_in = 5.0 #gCOD/L
		X_pr_in = 20.0 #gCOD/L
		X_li_in = 5.0 #gCOD/L
		X_suaa_in = 0 * 0.01 #g/L
		X_fa_in = 0 * 0.01 #g/L
		
		# Initial values of state variables 
		S_su_0 = 0.01 #gCOD/L
		S_aa_0 = 0.001 #gCOD/L
		S_fa_0 = 0.001 #gCOD/L
		S_ac_0 = 0.001 #gCOD/L
		X_c_0 = 2.0 #gCOD/L
		X_ch_0 = 5.0 #gCOD/L
		X_pr_0 = 20.0 #gCOD/L
		X_li_0 = 5.0 #gCOD/L
		X_suaa_0 = 0.01 #g/L
		X_fa_0 = 0.01 #g/L
	modelConcentrsRH2 = ModelConcentrsRH2()
	
	webModel = AttributeDict({
		'updateProgress' : lambda x, y : x, #:TRICKY: not used,
	})
	
	
	class ModelParamsRCH4:
		#Stoichiometric parameter values
		Y_ac = 0.05 #-
		
		#Biochemical parameter values
		k_m_ac = 8.0 #1/day
		K_S_ac = 0.15 #g/L
		
		Y_ch4_ac = 1.0 #-
		
		# Physical parameters
		V_liq_RCH4_del_V_liq_RH2 = 5.
	modelParamsRCH4 = ModelParamsRCH4()
	
	class ModelConcentrsRCH4:
		# Input concentrations 
		X_ac_in = 0 * 0.01 #g/L
		
		# Initial values of state variables 
		S_ac_0 = 0.2 #gCOD/L
		X_ac_0 = 0.76 #g/L
	modelConcentrsRCH4 = ModelConcentrsRCH4()		
	
	
	# Create the model
	bioreactor = ADM1H2CH4Bioreactors(
		webModel = webModel, 
		paramsRH2 = modelParamsRH2, 
		concentrsRH2 = modelConcentrsRH2,
		paramsRCH4 = modelParamsRCH4, 
		concentrsRCH4 = modelConcentrsRCH4,  
		initDataStorage = simulate)
	
	# Run simulation or load old results
	if (simulate == True):
		bioreactor.prepareSimulation(solverParams)
		bioreactor.run(solverParams)
	else:
		bioreactor.loadResult(simIndex = 1)
	
	# Export to csv file
	bioreactor.resultStorage.exportToCsv(fileName = csvFileName)
	
	# Plot results
	bioreactor.plotHDFResults()
	
	print "=== END: TestADM1H2Bioreactor ==="
	
	
if __name__ == '__main__':
	TestADM1H2CH4Bioreactor()
