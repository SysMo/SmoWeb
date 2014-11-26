from libcpp.string cimport string
from libcpp cimport bool
cimport CoolProp_Imports as CP

cdef class Fluid:
	cdef string fluidName
	cdef long fluidIndex
	cdef CP.Fluid* ptr
	
	def __cinit__(self, string fluidName):
		self.fluidName = fluidName
		self.fluidIndex = CP.get_Fluid_index(fluidName)
		if (self.fluidIndex == -1):
			raise ValueError('No fluid with name {0} found'.format(self.fluidName))
		self.ptr = CP.get_fluid(self.fluidIndex)

	def	BibTeXKey(self, item):
		validKeys = ["EOS", "CP0", "VISCOSITY", "CONDUCTIVITY",
					 "ECS_LENNARD_JONES", "ECS_FITS", "SURFACE_TENSION"]
		if (item not in validKeys):
			raise KeyError('BibTexKey must be one of ' + ', '.join(validKeys))
		return CP.get_BibTeXKey(self.fluidName, item)

	def EOSReference(self):
		return self.ptr.get_EOSReference()
		
	def TransportReference(self):
		return self.ptr.get_TransportReference()
	
	def CAS(self):
		return self.ptr.params.CAS
	
	def ASHRAE34(self):
		return self.ptr.environment.ASHRAE34
	
	def name(self):
		return self.fluidName
	
	def aliases(self):
		return self.ptr.get_aliases()
	
	def molarMass(self):
		return self.ptr.params.molemass;
		
	def accentricFactor(self):
		return self.ptr.params.accentricfactor
		
	def critical(self):
		return {
			'p': self.ptr.crit.p.Pa,
			'T': self.ptr.crit.T,
			'rho': self.ptr.crit.rho,
			'h': self.ptr.crit.h,
			's': self.ptr.crit.s,
			}
	
	def tripple(self):
		return {
			'p': self.ptr.params.ptriple,
			'T' : self.ptr.params.Ttriple,
			'rhoV': self.ptr.params.rhoVtriple,
			'rhoL': self.ptr.params.rhoLtriple,
			}
	
	def fluidLimits(self):
		return {
			'TMin': self.ptr.limits.Tmin, 
			'TMax': self.ptr.limits.Tmax, 
			'pMax': self.ptr.limits.pmax, 
			'rhoMax': self.ptr.limits.rhomax
			}
	
	def saturation_p(self, double p):
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

cdef class LiquidSaturationState:
	cdef FluidState state
	def __cinit__(self, FluidState state):		
		self.state = state


cdef class FluidState:
	cdef CP.CoolPropStateClassSI* ptr
	def __cinit__(self, fluid):		
		cdef string fluidName
		if (isinstance(fluid, str) or isinstance(fluid, unicode)):
			fluidName = fluid
			self.ptr = new CP.CoolPropStateClassSI(fluidName)
		elif (isinstance(fluid, Fluid)):
			self.ptr = new CP.CoolPropStateClassSI((<Fluid>fluid).ptr)
		else:
			raise TypeError('The argument of FluidState constructor must be either str or Fluid')
			
	def __dealloc__(self):
		del self.ptr
		
	def update(self, 
			string state1, double state1Value,
			string state2, double state2Value):
		cdef long p1Index = CP.get_param_index(state1)
		cdef long p2Index = CP.get_param_index(state2)
		self.ptr.update(p1Index, state1Value, p2Index, state2Value, -1, -1)

	def update_Tp(self, double T, double p):
		self.ptr.update(iT, T, iP, p, -1, -1)
	def update_Trho(self, double T, double rho):
		self.ptr.update(iT, T, iD, rho, -1, -1)	
	def update_prho(self, double p, double rho):
		self.ptr.update(iP, p, iD, rho, -1, -1)	
	def update_ph(self, double p, double h):
		self.ptr.update(iP, p, iH, h, -1, -1)	
	def update_ps(self, double p, double s):
		self.ptr.update(iP, p, iS, s, -1, -1)	
	def update_pq(self, double p, double q):
		self.ptr.update(iP, p, iQ, q, -1, -1)	
	def update_Tq(self, double T, double q):
		self.ptr.update(iT, T, iQ, q, -1, -1)	
		
	def T(self):
		return self.ptr.T()
	def p(self):
		return self.ptr.p()
	def rho(self):
		return self.ptr.rho()
	def h(self):
		return self.ptr.h()
	def q(self):
		if (self.ptr.TwoPhase):
			return self.ptr.Q()
		else:
			return -1.0;
	def isTwoPhase(self):
		return self.ptr.TwoPhase
	
	def s(self):
		return self.ptr.s()
	def u(self):
		return self.ptr.h() - self.ptr.p() / self.ptr.rho()
	def cp(self):
		return self.ptr.cp()
	def cv(self):
		return self.ptr.cv()
	
	def dpdt_v(self):
		cdef double _dpdt_v
		if (self.ptr.TwoPhase):
			_dpdt_v = self.dpdt_sat()
		else:
			_dpdt_v = self.ptr.dpdT_constrho()
		return _dpdt_v
	
	def dpdv_t(self):
		cdef double _dpdv_t
		if (self.ptr.TwoPhase):
			_dpdv_t = 0
		else:
			_dpdv_t = - self.ptr.rho() * self.ptr.rho() * self.ptr.dpdrho_constT();
		return _dpdv_t
		
	def dpdrho_t(self):
		cdef double _dpdrho_t
		if (self.ptr.TwoPhase):
			_dpdrho_t = 0
		else:
			_dpdrho_t = self.ptr.dpdrho_constT();
		return _dpdrho_t
		
	def dpdt_sat(self):
		return 1./self.ptr.dTdp_along_sat();

	def beta(self):
		if (not self.ptr.TwoPhase):
			return self.ptr.rho() * self.ptr.dvdT_constp()
		else:
			return 0
					
	def mu(self):
		return self.ptr.viscosity()
	def cond(self):
		return self.ptr.conductivity()
	def Pr(self):
		return self.ptr.Prandtl()
	def gamma(self):
		return self.ptr.cp() / self.ptr.cv();

