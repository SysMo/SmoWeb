from smo.media.CoolProp.CoolProp import FluidState
import numpy as np

class ThermodynamicProcess(object):
	def __init__(self, fluidName, eta = None, fQ = None):
		self.fluidName = fluidName
		self.initState = FluidState(fluidName)
		self.eta = eta
		self.fQ = fQ
		
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]
	
	def compute(self, finalStateVariable, finalStateVariableValue, mDot = None, initState = None):
		self.T_i = self.initState.T
		self.p_i = self.initState.p
		self.rho_i = self.initState.rho
		self.h_i = self.initState.h
		self.s_i = self.initState.s
		self.q_i = self.initState.q
		self.u_i = self.initState.u
		
		if self.constantStateVariable == 'S':
			if self.processType == 'expansion':
				finalState = IsentropicExpansion.compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot)
			elif self.processType == 'compresssion':
				finalState = IsentropicCompression.compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot)
		elif self.constantStateVariable == 'T':
			if self.processType == 'expansion':
				finalState = IsothermalExpansion.compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot)
			elif self.processType == 'compresssion':
				finalState = IsentropicCompression.compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot)
		elif self.constantStateVariable == 'H':
			if self.processType == 'expansion':
				finalState = IsenthalpicExpansion.compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot)
		elif self.constantStateVariable == 'P':
			finalState = HeatingCooling.compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot)
		
		# Read final state values
		self.T_f = finalState.T
		self.p_f = finalState.p
		self.rho_f = finalState.rho
		self.h_f = finalState.h
		self.s_f = finalState.s
		self.q_f = finalState.q
		self.u_f = finalState.u
			
		return finalState
		
	def draw(self, fig, finalStateVariable, finalStateVariableValue, numPoints = 10):
		if finalStateVariable != 'Q':
			stateVariableArr = np.logspace(np.log10(self.getStateValue(finalStateVariable, suffix="_i")), np.log10(finalStateVariableValue), num = numPoints)
		else:
			stateVariableArr = np.arange(self.getStateValue(finalStateVariable, suffix="_i"), finalStateVariableValue, numPoints)
			
		pArr = np.zeros(len(stateVariableArr))
		hArr = np.zeros(len(stateVariableArr))
		
		hArr[0] = self.initState.h
		pArr[0] = self.initState.p
		
		fState = self.initState
		for i in range(1, len(stateVariableArr)):
			fState = self.compute(finalStateVariable = finalStateVariable, 
							finalStateVariableValue = stateVariableArr[i], initState = fState)
			hArr[i] = fState.h
			pArr[i] = fState.p
		
		ax = fig.get_axes()[0]
		ax.semilogy(hArr/1e3, pArr/1e5, color = 'black', linewidth = 2)
		
		# State points
		ax.semilogy(hArr[0:1]/1e3, pArr[0:1]/1e5, 'ko')
		ax.semilogy(hArr[-1:]/1e3, pArr[-1:]/1e5, 'ko')
		
		if (self.constantStateVariable == 'P'):
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

class IsentropicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"
		self.constantStateVariable = 'S'
		
	def compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		finalState.update('S', self.s_i, finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		self.wReal = self.wIdeal * self.eta
		self.qOut = self.fQ * self.wReal
		
		# Real final state
		self.deltaH = self.wReal - self.qOut
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
		
		if mDot is not None:
			# Compute energy flows
			self.wDotIdeal = self.wIdeal * mDot
			self.wDotReal = self.wReal * mDot
			self.deltaHDot = self.deltaH * mDot
			self.qDotOut = self.qOut * mDot
		
		return finalState

class IsentropicCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"
		self.constantStateVariable = 'S'
		
	def compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		finalState.update('S', self.s_i, finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		self.wReal = self.wIdeal / self.eta
		self.qOut = self.fQ * self.wReal
		
		# Real final state
		self.deltaH = self.wReal - self.qOut
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
		
		if mDot is not None:
			# Compute energy flows
			self.wDotIdeal = self.wIdeal * mDot
			self.wDotReal = self.wReal * mDot
			self.deltaHDot = self.deltaH * mDot
			self.qDotOut = self.qOut * mDot
		
		return finalState
		
class IsothermalExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsothermalExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"
		self.constantStateVariable = 'T'
		
	def compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		finalState.update('T', self.T_i, finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		self.wReal = self.wIdeal * self.eta
		self.qOut = self.fQ * self.wReal
		
		# Real final state
		self.deltaH = self.wReal - self.qOut
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
		
		if mDot is not None:
			# Compute energy flows
			self.wDotIdeal = self.wIdeal * mDot
			self.wDotReal = self.wReal * mDot
			self.deltaHDot = self.deltaH * mDot
			self.qDotOut = self.qOut * mDot
		
		return finalState

class IsothermalCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsothermalCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"
		self.constantStateVariable = 'T'
		
	def compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		finalState.update('T', self.T_i, finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		self.wReal = self.wIdeal / self.eta
		self.qOut = self.wReal - self.wIdeal
		
		# Real final state
		self.deltaH = self.wReal - self.qOut
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
		
		if mDot is not None:
			# Compute energy flows
			self.wDotIdeal = self.wIdeal * mDot
			self.wDotReal = self.wReal * mDot
			self.deltaHDot = self.deltaH * mDot
			self.qDotOut = self.qOut * mDot
		
		return finalState
		
class IsenthalpicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsenthalpicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"
		self.constantStateVariable = 'H'
		
	def compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		finalState.update('H', self.h_i, finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		self.wReal = self.wIdeal * self.eta
		self.qOut = self.fQ * self.wReal
		
		# Real final state
		self.deltaH = self.wReal - self.qOut
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
		
		if mDot is not None:
			# Compute energy flows
			self.wDotIdeal = self.wIdeal * mDot
			self.wDotReal = self.wReal * mDot
			self.deltaHDot = self.deltaH * mDot
			self.qDotOut = self.qOut * mDot
		
		return finalState

class HeatingCooling(ThermodynamicProcess):
	def __init__(self, fluidName):
		super(HeatingCooling, self).__init__(fluidName)
		self.constantStateVariable = 'P'
		
	def compute_finalState(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		finalState.update('P', self.p_i, finalStateVariable, finalStateVariableValue)
		
		# Compute heat
		self.qOut = finalState.h - self.h_i
			
		if mDot is not None:
			# Compute heat flow
			self.qDotOut = self.qOut * mDot
		
		return finalState