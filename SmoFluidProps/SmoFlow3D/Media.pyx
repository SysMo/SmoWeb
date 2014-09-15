cimport SmoMedia as SM

cdef class Medium:
	cdef SM.Medium* ptr
	cdef int index
	
	sMediumAbstractType = SM.sMediumAbstractType
	sCompressibleFluidCoolProp = SM.sCompressibleFluidCoolProp
	sIncompressibleLiquidCoolProp = SM.sIncompressibleLiquidCoolProp 
	sSolidThermal = SM.sSolidThermal 

	@classmethod
	def create(cls, SM.MediumConcreteTypes mediumType, const char* mediumName, int mediumIndex):
		SM.Medium_register(mediumType, mediumName, mediumIndex)
		medium = Medium(mediumIndex)
		return medium
	
	def __cinit__(self, int index):
		self.index = index
		self.ptr = SM.Medium_get(index)
		
cdef class MediumState:
	cdef SM.MediumState* ptr
	
	def __cinit__(self, Medium medium):
		self.ptr = SM.MediumState_new(medium.ptr)
	def __dealloc__(self):
		del self.ptr
		
	def update_Tp(self, double T, double p):
		self.ptr.update_Tp(T, p)	
	def update_Trho(self, double T, double rho):
		self.ptr.update_Trho(T, rho)	
	def update_prho(self, double p, double rho):
		self.ptr.update_prho(p, rho)	
	def update_ph(self, double p, double h):
		self.ptr.update_ph(p, h)	
	def update_ps(self, double p, double s):
		self.ptr.update_ps(p, s)	
	def update_pq(self, double p, double q):
		self.ptr.update_pq(p, q)	
	def update_Tq(self, double T, double q):
		self.ptr.update_Tq(T, q)	

	def T(self):
		return self.ptr.T()
	def p(self):
		return self.ptr.p()
	def rho(self):
		return self.ptr.rho()
	def h(self):
		return self.ptr.h()
	
	def s(self):
		return self.ptr.s()
	def u(self):
		return self.ptr.u()
	def cp(self):
		return self.ptr.cp()
	def cv(self):
		return self.ptr.cv()
	def dpdt_v(self):
		return self.ptr.dpdt_v()
	def dpdv_t(self):
		return self.ptr.dpdv_t()
	def dpdrho_t(self):
		return self.ptr.dpdrho_t()
	def dvdt_p(self):
		return self.ptr.dvdt_p()
	def beta(self):
		return self.ptr.beta()
	def mu(self):
		return self.ptr.mu()
	def cond(self):
		return SM.MediumState_lambda(self.ptr)
	def Pr(self):
		return self.ptr.Pr()
	def gamma(self):
		return self.ptr.gamma()
	def R(self):
		return self.ptr.R()

	# Two-phase related functions
	# Gas mass fraction
	def q(self):
		return self.ptr.q()
	def isSupercritical(self):
		return self.ptr.isSupercritical()
	def isTwoPhase(self):
		return self.ptr.isTwoPhase()
	def deltaTSat(self):
		return self.ptr.deltaTSat()
	def TSat(self):
		return self.ptr.TSat()
	def dpdTSat(self):
		return self.ptr.dpdTSat()

	