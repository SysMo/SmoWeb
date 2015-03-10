from smo.media.CoolProp.CoolProp import FluidState
import numpy as np

class ThermodynamicProcess(object):
	def __init__(self, fluidName, eta = None, heatOutFraction = None):
		self.fluidName = fluidName
		self.initState = FluidState(fluidName)
		self.eta = eta
		self.heatOutFraction = heatOutFraction
		
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]
	
	def compute(self, finalStateVariable, finalStateVariableValue, mDot = None, initState = None):
		
		finalState = FluidState(self.fluidName)
		
		self.T_i = self.initState.T
		self.p_i = self.initState.p
		self.rho_i = self.initState.rho
		self.h_i = self.initState.h
		self.s_i = self.initState.s
		self.q_i = self.initState.q
		self.u_i = self.initState.u
		
		finalState.update(self.constantStateVariable, self.getStateValue(self.constantStateVariable, suffix="_i"),
							finalStateVariable, finalStateVariableValue)
		
		# Compute works and heat
		self.wIdeal = finalState.h - self.initState.h
		if self.processType == "compression":
			self.wReal = self.wIdeal / self.eta
			wExtra = self.wReal - self.wIdeal
		elif self.processType == "expansion":
			self.wReal = self.wIdeal * self.eta
			wExtra = self.wIdeal - self.wReal
		self.qOut = wExtra * self.heatOutFraction
		self.qFluid = wExtra * (1 - self.heatOutFraction)
		
		# Real final state
		self.deltaH = self.wIdeal + self.qFluid
		finalState.update(
			finalStateVariable, 
			finalStateVariableValue,
			'H',
			self.initState.h + self.deltaH
		)
			
		# Read final state values
		self.T_f = finalState.T
		self.p_f = finalState.p
		self.rho_f = finalState.rho
		self.h_f = finalState.h
		self.s_f = finalState.s
		self.q_f = finalState.q
		self.u_f = finalState.u

		if mDot is not None:
			# Compute energy flows
			self.wDotIdeal = self.wIdeal * mDot
			self.wDotReal = self.wReal * mDot
			self.deltaHDot = self.deltaH * mDot
			self.qDotOut = self.qOut * mDot
			self.qDotFluid = self.qFluid * mDot
			
		return finalState
		
	def draw(self, fig, finalStateVariable, finalStateVariableValue, numPoints = 5):
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
		
		print hArr/1e3
		print pArr/1e5
		ax = fig.get_axes()[0]
		ax.semilogy(hArr/1e3, pArr/1e5, color = 'black', linewidth = 2)
		
		return fig

class IsentropicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"
		self.constantStateVariable = 'S'

class IsentropicCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"
		self.constantStateVariable = 'S'
		
class IsothermalExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsothermalExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"
		self.constantStateVariable = 'T'

class IsothermalCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsothermalCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"
		self.constantStateVariable = 'T'
		
class IsenthalpicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsenthalpicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"
		self.constantStateVariable = 'H'

class HeatingCooling(ThermodynamicProcess):
	def __init__(self, fluidName):
		super(HeatingCooling, self).__init__(fluidName)
		self.constantStateVariable = 'P'
	
	def compute(self, finalStateVariable, finalStateVariableValue, mDot = None, initState = None):
		finalState = FluidState(self.fluidName)
		
		if initState is None:
			initState = self.initState
		
		self.T_i = initState.T
		self.p_i = initState.p
		self.rho_i = initState.rho
		self.h_i = initState.h
		self.s_i = initState.s
		self.q_i = initState.q
		self.u_i = initState.u
		
		finalState.update('P', self.p_i, finalStateVariable, finalStateVariableValue)
		
		# Read final state values
		self.T_f = finalState.T
		self.p_f = finalState.p
		self.rho_f = finalState.rho
		self.h_f = finalState.h
		self.s_f = finalState.s
		self.q_f = finalState.q
		self.u_f = finalState.u
		
		# Compute heat
		self.qOut = self.h_f - self.h_i
		
		if mDot is not None:
			# Compute heat flow
			self.qDotOut = self.qOut * mDot
		
		return finalState	