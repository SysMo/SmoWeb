from smo.media.CoolProp.CoolProp import FluidState

class ThermodynamicProcess(object):
	def __init__(self, fluidName, eta = None, heatOutFraction = None):
		self.fluidName = fluidName
		self.initState = FluidState(fluidName)
		self.eta = eta
		self.heatOutFraction = heatOutFraction
		
	def getStateValue(self, sVar, prefix = "", suffix=""):
		sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
		return self.__dict__[prefix + sVarDict[sVar] + suffix]
	
	def compute(self, constantStateVariable, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		
		self.T_i = self.initState.T
		self.p_i = self.initState.p
		self.rho_i = self.initState.rho
		self.h_i = self.initState.h
		self.s_i = self.initState.s
		self.q_i = self.initState.q
		self.u_i = self.initState.u
		
		finalState.update(constantStateVariable, self.getStateValue(constantStateVariable, suffix="_i"),
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

		# Compute energy flows
		self.wDotIdeal = self.wIdeal * mDot
		self.wDotReal = self.wReal * mDot
		self.deltaHDot = self.deltaH * mDot
		self.qDotOut = self.qOut * mDot
		self.qDotFluid = self.qFluid * mDot

class IsentropicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"

class IsentropicCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsentropicCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"
		
class IsothermalExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsothermalExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"

class IsothermalCompression(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsothermalCompression, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "compression"
		
class IsenthalpicExpansion(ThermodynamicProcess):
	def __init__(self, fluidName, eta, heatOutFraction):
		super(IsenthalpicExpansion, self).__init__(fluidName, eta, heatOutFraction)
		self.processType = "expansion"

class HeatingCooling(ThermodynamicProcess):
	def __init__(self, fluidName):
		super(HeatingCooling, self).__init__(fluidName)
	
	def compute(self, finalStateVariable, finalStateVariableValue, mDot):
		finalState = FluidState(self.fluidName)
		
		self.T_i = self.initState.T
		self.p_i = self.initState.p
		self.rho_i = self.initState.rho
		self.h_i = self.initState.h
		self.s_i = self.initState.s
		self.q_i = self.initState.q
		self.u_i = self.initState.u
		
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
		
		# Compute heat flow
		self.qDotOut = self.qOut * mDot