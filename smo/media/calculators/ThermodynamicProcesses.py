from smo.media.CoolProp.CoolProp import FluidState
import numpy as np

class ProcessCharacteristics(object):
	def __init__(self):
		self.wIdeal = 0
		self.wReal = 0
		self.delta_h = 0
		self.qIn = 0
	
class ProcessFlows(object):
	def __init__(self):
		self.wDotIdeal = 0
		self.wDotReal = 0
		self.deltaHDot = 0
		self.qDotIn = 0

	def compute(self, pChars, mDot):
		self.wDotIdeal = mDot * pChars.wIdeal
		self.wDotReal = mDot * pChars.wReal
		self.deltaHDot = mDot * pChars.delta_h
		self.qDotIn = mDot * pChars.qIn
		


class ThermodynamicProcess(object):
	def __init__(self, fluidName):
		self.fluidName = fluidName
		self.initialState = FluidState(fluidName)
		self.finalState = FluidState(fluidName)
		self.flows = ProcessFlows()
		
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]
	
	def computeIntermediateStateDistribution(self, stateVar, stateVal, numPoints):
		raise NotImplementedError("The concrete classes inheriting from 'ThermodynamicProcess' must implement 'computeIntermediateStateDistribution' method")		
	
	def computeNextState(self, fCurrent, fNext, stateVar, stateVal):
		raise NotImplementedError("The concrete classes inheriting from 'ThermodynamicProcess' must implement 'computeNextState' method")
	
	def compute(self, stateVar, stateVal, mDot = None, numIntermediateStates = 0):
		"""
		The intermediate states only work for some special cases. Generally the final state computed with and without intermediate states is different
		"""
		self.chars = self.computeNextState(self.initialState, self.finalState, stateVar, stateVal)
		if (mDot is not None):
			self.flows.compute(self.chars, mDot)
		(iStateVar, valueList) = self.computeIntermediateStateDistribution(stateVar, stateVal, numPoints = numIntermediateStates + 2)
		self.fStates = [self.initialState]
		# Create and calculate intermediate states
		for i in range(numIntermediateStates):
			newState = FluidState(self.fluidName)
			self.computeNextState(self.fStates[-1], newState, iStateVar, valueList[i + 1])
			self.fStates.append(newState)
		self.fStates.append(self.finalState)
		
	def draw(self, fig, numPoints = 10):			
		pArr = np.zeros(len(self.fStates))
		hArr = np.zeros(len(self.fStates))
		
		for i in range(len(self.fStates)):
			hArr[i] = self.fStates[i].h
			pArr[i] = self.fStates[i].p
		
		ax = fig.get_axes()[0]
		ax.semilogy(hArr/1e3, pArr/1e5, 'k.-', linewidth = 2)
		
		# State points
		ax.semilogy(hArr[0:1]/1e3, pArr[0:1]/1e5, 'ko')
		ax.semilogy(hArr[-1:]/1e3, pArr[-1:]/1e5, 'ko')
		
		if (isinstance(self, IsobaricProcess)):
			xytext=(0, 7)
		else:
			xytext=(7, 0)
		
		ax.annotate('1', 
					xy = (hArr[0]/1e3, pArr[0]/1e5),
 					xytext=xytext,
 					textcoords='offset points')
		ax.annotate('2',
					xy = (hArr[-1]/1e3, pArr[-1]/1e5),
 					xytext=xytext,
 					textcoords='offset points')
		return fig

################# Compression/Expansion ######################
class CompressionExpansion(ThermodynamicProcess):
	def computeIntermediateStateDistribution(self, stateVar, stateVal, numPoints):
		if (stateVar == 'P'):
			return 'P', np.logspace(np.log10(self.initialState.p), np.log10(stateVal), num = numPoints)
		else:
			raise ValueError('The final state for compression/expansion process must be defined by pressure')

class IsentropicProcess(CompressionExpansion):
	def __init__(self, fluid, eta, fQ):
		"""
		parameters:
		:param fluid: working fluid
		:param eta: isentropic efficiency
		:param fQ: heat loss factor = QDot / WDot 
		"""
		super(IsentropicProcess, self).__init__(fluid)
		self.eta = eta
		self.fQ = fQ
		

	def computeNextState(self, fCurrent, fNext, stateVar, stateVal):
		fNext.update('S', fCurrent.s, stateVar, stateVal)
		ch = ProcessCharacteristics()
		# Compute works and heat
		ch.wIdeal = fNext.h - fCurrent.h
		if (fNext.p > fCurrent.p):			
			ch.wReal = ch.wIdeal / self.eta
		else:
			ch.wReal = ch.wIdeal * self.eta
		ch.qIn = - self.fQ * ch.wReal
		
		# Real final state
		ch.delta_h = ch.wReal + ch.qIn
		fNext.update_ph(stateVal, fCurrent.h + ch.delta_h)
		
		return ch

		
class IsothermalProcess(CompressionExpansion):
	def __init__(self, fluidName, eta, fQ):
		super(IsothermalProcess, self).__init__(fluidName)
		self.eta = eta
		self.fQ = fQ
		
	def computeNextState(self, fCurrent, fNext, stateVar, stateVal):
		fNext.update('T', fCurrent.T, stateVar, stateVal)
		ch = ProcessCharacteristics()
		# Compute works and heat
		qInIdeal = fCurrent.T * (fNext.s - fCurrent.s)
		ch.wIdeal = (fNext.h - fCurrent.h) - qInIdeal
		if (fNext.p > fCurrent.p):
			ch.wReal = ch.wIdeal / self.eta
		else:
			ch.wReal = ch.wIdeal * self.eta
		
		# Real final state
		ch.qIn = qInIdeal * self.fQ
		ch.delta_h = ch.wReal + ch.qIn
		fNext.update_ph(stateVal, fCurrent.h + ch.delta_h)
		
		return ch
		
class IsenthalpicExpansion(CompressionExpansion):
	def __init__(self, fluidName):
		super(IsenthalpicExpansion, self).__init__(fluidName)
		
	def computeNextState(self, fCurrent, fNext, stateVar, stateVal):
		if (stateVal > fCurrent.p):
			raise ValueError('For isenthalpic expansion the final pressure must be lower than the initial pressure.')
		fNext.update('H', fCurrent.h, stateVar, stateVal)
		ch = ProcessCharacteristics()
		return ch

################# Heating/Cooling ######################		
class HeatingCooling(ThermodynamicProcess):
	def computeIntermediateStateDistribution(self, stateVar, stateVal, numPoints):
		if (stateVar in ['T', 'Q', 'H'] or stateVar == 'Q'):
			return 'H', np.logspace(np.log10(self.initialState.h), np.log10(self.finalState.h), num = numPoints)
		else:
			raise ValueError('The final state for compression/expansion process must be defined by temperature or vapor quality')

class IsobaricProcess(HeatingCooling):
	def __init__(self, fluidName):
		super(HeatingCooling, self).__init__(fluidName)
		self.constantStateVariable = 'P'
		
	def computeNextState(self, fCurrent, fNext, stateVar, stateVal):
		fNext.update('P', fCurrent.p, stateVar, stateVal)
		ch = ProcessCharacteristics()
		# Compute heat
		ch.wIdeal = 0
		ch.wReal = 0
		ch.delta_h = fNext.h - fCurrent.h
		ch.qIn = ch.delta_h

		return ch
