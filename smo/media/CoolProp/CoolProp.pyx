from libcpp.string cimport string
from libcpp cimport bool
from numpy.math cimport INFINITY
cimport CoolProp_Imports as CP

cdef class Fluid:
	""" 
	Class representing a CoolProp fluid
	"""
	cdef string fluidName
	cdef long fluidIndex
	cdef CP.Fluid* ptr
	
	def __init__(self, fluidName):
		"""__init__(fluidName)
		:param fluidName: name of fluid
		"""
		pass
		
	def __cinit__(self, string fluidName):
		self.fluidName = fluidName
		self.fluidIndex = CP.get_Fluid_index(fluidName)
		if (self.fluidIndex == -1):
			raise ValueError('No fluid with name {0} found'.format(self.fluidName))
		self.ptr = CP.get_fluid(self.fluidIndex)

	def	BibTeXKey(self, item):
		""" BibTeXKey(item)
		Bibliographic info """
		validKeys = ["EOS", "CP0", "VISCOSITY", "CONDUCTIVITY",
					 "ECS_LENNARD_JONES", "ECS_FITS", "SURFACE_TENSION"]
		if (item not in validKeys):
			raise KeyError('BibTexKey must be one of ' + ', '.join(validKeys))
		return CP.get_BibTeXKey(self.fluidName, item)

	property EOSReference:
		"""equation of state source"""
		def __get__(self):
			return self.ptr.get_EOSReference()
			
	property TransportReference:
		"""transport properties source"""
		def __get__(self):
			return self.ptr.get_TransportReference()
		
	property CAS:
		""""""
		def __get__(self):
			return self.ptr.params.CAS
		
	property ASHRAE34:
		""""""
		def __get__(self):
			return self.ptr.environment.ASHRAE34
		
	property name:
		"""name of fluid"""
		def __get__(self):
			return self.fluidName
		
	property aliases:
		""""""
		def __get__(self):
			return self.ptr.get_aliases()
		
	property molarMass:
		""""""
		def __get__(self):
			return self.ptr.params.molemass;
			
	property accentricFactor:
		""""""
		def __get__(self):
			return self.ptr.params.accentricfactor
			
	property critical:
		"""dictionary of critial point values - p, T, rho, h, s"""
		def __get__(self):
			return {
				'p': self.ptr.crit.p.Pa,
				'T': self.ptr.crit.T,
				'rho': self.ptr.crit.rho,
				'h': self.ptr.crit.h,
				's': self.ptr.crit.s,
				}
		
	property tripple:
		"""dictionary of tripple point values - p, T, rhoV, rhoL"""
		def __get__(self):
			return {
				'p': self.ptr.params.ptriple,
				'T' : self.ptr.params.Ttriple,
				'rhoV': self.ptr.params.rhoVtriple,
				'rhoL': self.ptr.params.rhoLtriple,
				}
		
	property fluidLimits:
		"""fluid limits - TMin, TMax, pMax, rhoMax"""
		def __get__(self):
			return {
				'TMin': self.ptr.limits.Tmin, 
				'TMax': self.ptr.limits.Tmax, 
				'pMax': self.ptr.limits.pmax, 
				'rhoMax': self.ptr.limits.rhomax
				}
	
	def saturation_p(self, double p):
		"""saturation_p(p)
		Computes saturation properties at given pressure\n
		Returns dictionary of values - TsatL, TsatV, rhoL, rhoV
		"""
		cdef double TsatLout = 0
		cdef double TsatVout = 0
		cdef double rhoLout = 0
		cdef double rhoVout = 0
		self.ptr.saturation_p(p, False, TsatLout, TsatVout, rhoLout, rhoVout)
		return {
			'TsatL': TsatLout, 
			'TsatV': TsatVout, 
			'rhoL': rhoLout, 
			'rhoV': rhoVout
			}

	def saturation_T(self, double T):
		"""saturation_T(T)
		Computes saturation properties at given temperature\n
		Returns dictionary of values - psatL, psatV, rhoL, rhoV
		"""
		cdef double psatLout = 0
		cdef double psatVout = 0
		cdef double rhoLout = 0
		cdef double rhoVout = 0
		self.ptr.saturation_T(T, False, psatLout, psatVout, rhoLout, rhoVout)
		return {
			'psatL': psatLout, 
			'psatV': psatVout, 
			'rhoL': rhoLout, 
			'rhoV': rhoVout
			}

cdef long iP = CP.get_param_index('P')
cdef long iT = CP.get_param_index('T')
cdef long iD = CP.get_param_index('D')
cdef long iH = CP.get_param_index('H')
cdef long iS = CP.get_param_index('S')
cdef long iQ = CP.get_param_index('Q')

# cdef class LiquidSaturationState:
# 	cdef FluidState state
# 	def __cinit__(self, FluidState state):		
# 		self.state = state

cdef class FluidState:
	cdef CP.SmoFlow_CoolPropState* ptr

	def __init__(self, fluid):
		"""__init__(fluid)
		:param fluid: name of fluid or :class:`Fluid` object
		"""
		pass
	
	def __cinit__(self, fluid):		
		cdef string fluidName
		# From fluid name
		if (isinstance(fluid, str) or isinstance(fluid, unicode)):
			fluidName = fluid
			self.ptr = new CP.SmoFlow_CoolPropState(fluidName)
		# From fluid object
		elif (isinstance(fluid, Fluid)):
			self.ptr = new CP.SmoFlow_CoolPropState((<Fluid>fluid).ptr)
		else:
			raise TypeError('The argument of FluidState constructor must be either str or Fluid')
			
	def __dealloc__(self):
		del self.ptr

	property T:
		"""temperature"""	
		def __get__(self):
			return self.ptr.T()
	property p:
		"""pressure"""	
		def __get__(self):
			return self.ptr.p()
	property rho:
		"""density"""	
		def __get__(self):
			return self.ptr.rho()
	property h:
		"""specific enthalpy"""	
		def __get__(self):
			return self.ptr.h()
	property q:
		"""vapor quality"""	
		def __get__(self):
			if (self.ptr.TwoPhase):
				return self.ptr.Q()
			else:
				return -1.0;

	def isTwoPhase(self):
		"""Checks if state is in the two-phase region\n
		Returns bool"""
		return self.ptr.TwoPhase
	
	property s:
		"""specific entropy"""	
		def __get__(self):
			return self.ptr.s()
	property u:
		"""specific internal energy"""	
		def __get__(self):
			return self.ptr.h() - self.ptr.p() / self.ptr.rho()
	property cp:
		"""specific heat capacity at constant pressure"""	
		def __get__(self):
			return self.ptr.cp()
	property cv:
		"""specific heat capacity at constant volume"""	
		def __get__(self):
			return self.ptr.cv()

####################################################################
# Functions safe to use in 2-phase
	property dvdp_T:
		""""""
		def __get__(self):		
			cdef double _dvdp_constT
			if (self.ptr.TwoPhase):
				_dvdp_constT = INFINITY
			else:
				_dvdp_constT = self.ptr.dvdp_constT()
			return _dvdp_constT

	property dvdT_p:
		""""""
		def __get__(self):		
			cdef double _dvdT_constp
			if (self.ptr.TwoPhase):
				_dvdT_constp = INFINITY
			else:
				_dvdT_constp = self.ptr.dvdT_constp()
			return _dvdT_constp
####################################################################
	property dpdt_v:
		""""""	
		def __get__(self):		
			cdef double _dpdt_v
			if (self.ptr.TwoPhase):
				_dpdt_v = self.dpdt_sat
			else:
				_dpdt_v = self.ptr.dpdT_constrho()
			return _dpdt_v
		
	property dpdv_t:
		""""""	
		def __get__(self):		
			cdef double _dpdv_t
			if (self.ptr.TwoPhase):
				_dpdv_t = 0
			else:
				_dpdv_t = - self.ptr.rho() * self.ptr.rho() * self.ptr.dpdrho_constT();
			return _dpdv_t
			
	property dpdrho_t:
		""""""	
		def __get__(self):
			return self.ptr.dpdrho_constT()
####################################################################
##### New derivatives #####
	property dsdp_t:
			""""""
			def __get__(self):		
				cdef double _dsdp_constT
				if (self.ptr.TwoPhase):
					_dsdp_constT = INFINITY
				else:
					_dsdp_constT = self.ptr.dsdp_constT()
				return _dsdp_constT
	
	property dhdt_p:
			""""""
			def __get__(self):		
				cdef double _dhdT_constp
				if (self.ptr.TwoPhase):
					_dhdT_constp = INFINITY
				else:
					_dhdT_constp = self.ptr.dhdT_constp()
				return _dhdT_constp
	
	property dpdt_h:
			""""""
			def __get__(self):		
				cdef double _dpdT_consth
				if (self.ptr.TwoPhase):
					_dpdT_consth = self.dpdt_sat
				else:
					_dpdT_consth = self.ptr.dpdT_consth()
				return _dpdT_consth
	
	property dsdt_v:
			""""""
			def __get__(self):		
				cdef double _dsdT_constv
				if (self.ptr.TwoPhase):
					_dsdT_constv = (self.getSatV()["s"] - self.getSatL()["s"]) * \
									(self.q * (self.rho**2) * self.ptr.drhodT_along_sat_vapor() +
										(1 - self.q) * (self.rho**2) * self.ptr.drhodT_along_sat_liquid()
									) / (1. / self.getSatV()["rho"] - 1. / self.getSatL()["rho"]) + \
									(self.q * self.ptr.dsdT_along_sat_vapor() + 
										(1 - self.q) * self.ptr.dsdT_along_sat_liquid()
									)
				else:
					_dsdT_constv = self.ptr.dsdT_constrho()
				return _dsdT_constv
			
# 	property drhodp_h:
# 			""""""
# 			def __get__(self):		
# 				cdef double _drhodp_consth
# 				if (self.ptr.TwoPhase):
# 					_drhodp_consth = INFINITY
# 				else:
# 					_drhodp_consth = self.ptr.drhodp_consth()
# 				return _drhodp_consth
# 	
# 	property drhodh_p:
# 			""""""
# 			def __get__(self):		
# 				cdef double _drhodh_constp
# 				if (self.ptr.TwoPhase):
# 					pass
# 				else:
# 					_drhodh_constp = self.ptr.drhodh_constp()
# 				return _drhodh_constp
####################################################################
####################################################################
####################################################################
			
	property dpdt_sat:
		""""""	
		def __get__(self):
			return 1./self.ptr.dTdp_along_sat();
	property beta:
		"""isobaric thermal expansivity"""	
		def __get__(self):
			if (not self.ptr.TwoPhase):
				return self.ptr.rho() * self.ptr.dvdT_constp()
			else:
				return 0
	property mu:
		"""dynamic viscosity"""					
		def __get__(self):
			return self.ptr.viscosity()
	property cond:
		"""thermal conductivity"""
		def __get__(self):
			return self.ptr.conductivity()
	property Pr:
		"""Prandtl number"""
		def __get__(self):
			return self.ptr.Prandtl()
	property gamma:
		"""cp / cv"""
		def __get__(self):
			return self.ptr.gamma();

	def update(self, 
			string state1, double state1Value,
			string state2, double state2Value):
		"""update(state1, state1Value, state2, state2Value)
		:param state1: name of first state variable
		:param state1Value: value of first state variable
		:param state2: name of second state variable
		:param state2Value: value of second state variable
		
		Updates fluid state by two state variables.
		"""
		cdef long p1Index = CP.get_param_index(state1)
		cdef long p2Index = CP.get_param_index(state2)
		self.ptr.update(p1Index, state1Value, p2Index, state2Value, -1, -1)
	def update_Tp(self, double T, double p):
		"""update_Tp(T, p)
		:param T: temperature
		:param p: pressure
		
		Updates fluid state by temperature and presure
		
		"""
		self.ptr.update(iT, T, iP, p, -1, -1)
	def update_Trho(self, double T, double rho):
		"""update_Trho(T, rho)
		:param T: temperature
		:param rho: density
		
		Updates fluid state by temperature and density
		"""
		self.ptr.update(iT, T, iD, rho, -1, -1)	
	def update_Ts(self, double T, double s):
		"""update_Ts(T, s)
		:param T: temperature
		:param s: specific entropy
		
		Updates fluid state by temperature and specific entropy
		"""
		self.ptr.update(iT, T, iS, s, -1, -1)	
	def update_prho(self, double p, double rho):
		"""update_prho(p, rho)
		:param p: pressure
		:param rho: density
		
		Updates fluid state by pressure and density
		"""
		self.ptr.update(iP, p, iD, rho, -1, -1)	
	def update_ph(self, double p, double h):
		"""update_ph(p, h)
		:param p: pressure
		:param h: specific enthalpy
		
		Updates fluid state by pressure and specific enthalpy
		"""
		self.ptr.update(iP, p, iH, h, -1, -1)	
	def update_ps(self, double p, double s):
		"""update_ps(p, s)
		:param p: pressure
		:param s: specific entropy
		
		Updates fluid state by pressure and specific entropy
		"""
		self.ptr.update(iP, p, iS, s, -1, -1)	
	def update_pq(self, double p, double q):
		"""update_pq(p, q)
		:param p: pressure
		:param q: vapor quality
		
		Updates fluid state by pressure and vapor quality
		"""
		self.ptr.update(iP, p, iQ, q, -1, -1)	
	def update_Tq(self, double T, double q):
		"""update_Tq(T, q)
		:param T: temperature
		:param q: vapor quality
		
		Updates fluid state by temperature and vapor quality
		"""
		self.ptr.update(iT, T, iQ, q, -1, -1)
		
	def getSatL(self):
		"""Returns dictionary of saturation properties in the liquid phase - rho, s, h"""
		#cdef CP.CoolPropStateClassSI* satL
		if (self.isTwoPhase()):
			satL = self.ptr.getSatL()
			return {
				'rho': 	satL.rho(),
				's':	satL.s(),
				'h':	satL.h()
			}
		else:
			return None

	def getSatV(self):
		"""Returns dictionary of saturation properties in the vapor phase - rho, s, h"""
		#cdef CP.CoolPropStateClassSI* satV
		if (self.isTwoPhase()):
			satV = self.ptr.getSatV()
			return {
				'rho': 	satV.rho(),
				's':	satV.s(),
				'h':	satV.h()

			}
		else:
			return None
