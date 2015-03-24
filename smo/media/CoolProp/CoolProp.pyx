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
			return self.ptr.params.molemass
			
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

#============================================================================

cdef class SaturationState:
	cdef CP.CoolPropStateClassSI* ptr
	cdef CP.SmoFlow_CoolPropState* parent

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
	
	property v:
		"""specific volume"""	
		def __get__(self):
			return 1./self.ptr.rho()

	property h:
		"""specific enthalpy"""	
		def __get__(self):
			return self.ptr.h()
	
	property s:
		"""specific enthalpy"""	
		def __get__(self):
			return self.ptr.s()

	property q:
		"""vapor quality"""	
		def __get__(self):
			return self.ptr.Q()

cdef class SaturationStateLiquid(SaturationState):
	def __cinit__(self, FluidState fs):
		self.parent = fs.ptr
		self.ptr = fs.ptr.getSatL()
		
	property drhodT:
		def __get__(self):
			return self.parent.drhodT_along_sat_liquid()

	property drhodp:
		def __get__(self):
			return self.parent.drhodp_along_sat_liquid()

	property dvdT:
		def __get__(self):
			return -1./(self.rho * self.rho) * self.parent.drhodT_along_sat_liquid()

	property dvdp:
		def __get__(self):
			return -1./(self.rho * self.rho) * self.parent.drhodp_along_sat_liquid()

	property dsdT:
		def __get__(self):
			return self.parent.dsdT_along_sat_liquid()

	property dsdp:
		def __get__(self):
			return self.parent.dsdp_along_sat_liquid()

	property dhdT:
		def __get__(self):
			return self.parent.dhdT_along_sat_liquid()

	property dhdp:
		def __get__(self):
			return self.parent.dhdp_along_sat_liquid()

cdef class SaturationStateVapor(SaturationState):
	def __cinit__(self, FluidState fs):
		self.parent = fs.ptr
		self.ptr = fs.ptr.getSatV()

	property drhodT:
		def __get__(self):
			return self.parent.drhodT_along_sat_vapor()

	property drhodp:
		def __get__(self):
			return self.parent.drhodp_along_sat_vapor()

	property dvdT:
		def __get__(self):
			return -1./(self.rho * self.rho) * self.parent.drhodT_along_sat_vapor()

	property dvdp:
		def __get__(self):
			return -1./(self.rho * self.rho) * self.parent.drhodp_along_sat_vapor()

	property dsdT:
		def __get__(self):
			return self.parent.dsdT_along_sat_vapor()

	property dsdp:
		def __get__(self):
			return self.parent.dsdp_along_sat_vapor()

	property dhdT:
		def __get__(self):
			return self.parent.dhdT_along_sat_vapor()

	property dhdp:
		def __get__(self):
			return self.parent.dhdp_along_sat_vapor()

#============================================================================

cdef long iP = CP.get_param_index('P')
cdef long iT = CP.get_param_index('T')
cdef long iD = CP.get_param_index('D')
cdef long iH = CP.get_param_index('H')
cdef long iS = CP.get_param_index('S')
cdef long iQ = CP.get_param_index('Q')

cdef class FluidState:
	cdef CP.SmoFlow_CoolPropState* ptr
	cdef public SaturationStateLiquid _SatL
	cdef public SaturationStateVapor _SatV
	cdef Fluid fluid
	cdef bool updated

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
			self.fluid = Fluid(fluid)
			self.ptr = new CP.SmoFlow_CoolPropState(fluidName)
		# From fluid object
		elif (isinstance(fluid, Fluid)):
			self.fluid = fluid
			self.ptr = new CP.SmoFlow_CoolPropState((<Fluid>fluid).ptr)
		else:
			raise TypeError('The argument of FluidState constructor must be either str or Fluid')
		
		self._SatL = SaturationStateLiquid(self)
		self._SatV = SaturationStateVapor(self)
		self.updated = False
			
	def __dealloc__(self):
		del self.ptr

	def checkUpdated(self):
		if (not self.updated):
			raise RuntimeError("In order to read a property, you must first call one of the 'update' functions")

	property fluid:
		"""fluid"""
		def __get__(self):
			return self.fluid
		
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
	
	property v:
		"""specific volume"""	
		def __get__(self):
			return 1./self.ptr.rho()

	property h:
		"""specific enthalpy"""	
		def __get__(self):
			return self.ptr.h()
	
	property q:
		"""vapor quality"""	
		def __get__(self):
			return self.ptr.q()

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
			return self.ptr.u()
	
	property cp:
		"""specific heat capacity at constant pressure"""	
		def __get__(self):
			return self.ptr.cp()
	
	property cv:
		"""specific heat capacity at constant volume"""	
		def __get__(self):
			return self.ptr.cv()

####################################################################
# Two-phase-safe derivatives
	property dvdp_T:
		""""""
		def __get__(self):		
			return self.ptr.dvdp_constT()

	property dvdT_p:
		""""""
		def __get__(self):		
			return self.ptr.dvdT_constp()
				
	property dpdrho_T:
		""""""	
		def __get__(self):
			return self.ptr.dpdrho_constT()
		
	property dpdT_v:
		""""""	
		def __get__(self):		
			return self.ptr.dpdT_constv()
		
	property dvds_T:
		""""""	
		def __get__(self):		
			return 1. / self.ptr.dpdT_constv()
		
	property dpdv_T:
		""""""	
		def __get__(self):		
			return self.ptr.dpdv_constT()
			
	property dsdp_T:
			""""""
			def __get__(self):		
				return self.ptr.dsdp_constT()
	
	property dhdT_p:
			""""""
			def __get__(self):		
				return self.ptr.dhdT_constp()
	
	property dpdT_h:
			""""""
			def __get__(self):		
				return self.ptr.dpdT_consth()
	
	property dsdT_v:
			""""""
			def __get__(self):		
				return self.ptr.dsdT_constv()

####################################################################
# Two-phase specific derivatives
	property dpdT_sat:
		""""""	
		def __get__(self):
			return self.ptr.dpdT_sat()

	property dsdq_T: 
		""""""
		def __get__(self):
			return self.ptr.dsdq_constT()

	property dsdT_q: 
		""""""
		def __get__(self):
			return self.ptr.dsdT_constq()

	property dvdT_q: 
		""""""
		def __get__(self):
			return self.ptr.dvdT_constq()

	property dvdq_T: 
		""""""
		def __get__(self):
			return self.ptr.dvdq_constT()

	property dqdT_v:
		""""""
		def __get__(self):
			return self.ptr.dqdT_constv()
####################################################################
####################################################################
				
	property beta:
		"""isobaric thermal expansivity"""	
		def __get__(self):
			return self.ptr.beta()
	
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
		"""heat capacity ratio"""
		def __get__(self):
			return self.ptr.gamma()
	
	#########################################	
	# Extra properties
	def b(self, double TExt):
		return self.ptr.h() - TExt * self.ptr.s()
	
	
	#########################################
	# Update methods
		
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
		cdef long p1Index
		cdef long p2Index
		cdef double TSat
		
		if (state1.compare("dT") == 0 and state2.compare("P") == 0):
			TSat = self.fluid.saturation_p(state2Value)['TsatL']
			self.ptr.update(iT, TSat + state1Value, iP, state2Value, -1, -1)
		elif (state1.compare("P") == 0 and state2.compare("dT") == 0):
			TSat = self.fluid.saturation_p(state1Value)['TsatL']
			self.ptr.update(iT, TSat + state2Value, iP, state1Value, -1, -1)
		else:
			p1Index = CP.get_param_index(state1)
			p2Index = CP.get_param_index(state2)
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

	property SatL:
		"""Saturated liquid object"""
		def __get__(self):
			return self._SatL
	
	property SatV:
		"""Saturated vapor object"""
		def __get__(self):
			return self._SatV
	
# 	def getSatL(self):
# 		"""Returns dictionary of saturation properties in the liquid phase - rho, s, h"""
# 		#cdef CP.CoolPropStateClassSI* satL
# 		if (self.isTwoPhase()):
# 			satL = self.ptr.getSatL()
# 			return {
# 				'rho': 	satL.rho(),
# 				's':	satL.s(),
# 				'h':	satL.h()
# 			}
# 		else:
# 			return None
# 
# 	def getSatV(self):
# 		"""Returns dictionary of saturation properties in the vapor phase - rho, s, h"""
# 		#cdef CP.CoolPropStateClassSI* satV
# 		if (self.isTwoPhase()):
# 			satV = self.ptr.getSatV()
# 			return {
# 				'rho': 	satV.rho(),
# 				's':	satV.s(),
# 				'h':	satV.h()
# 
# 			}
# 		else:
# 			return None
