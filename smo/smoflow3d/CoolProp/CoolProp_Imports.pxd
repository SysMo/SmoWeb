from libcpp.string cimport string
from libcpp cimport bool

cdef extern from "CoolProp/CoolProp.h":
	cdef cppclass PressureUnit:
		double Pa
	
	cdef cppclass HSContainer:
		double hmax,T_hmax,rho_hmax,s_hmax, sV_Tmin, sL_Tmin, hV_Tmin, hL_Tmin
	
	cdef cppclass OtherParameters:
		double molemass, Ttriple, ptriple, accentricfactor, R_u, rhoVtriple, rhoLtriple
		string CAS
		string HSReferenceState
	
	cdef cppclass CriticalStruct:
		double rho, T, v, h, s, rhobar
		PressureUnit p
	
	cdef cppclass FluidLimits:
		double Tmin, Tmax, pmax, rhomax;	
	
	cdef cppclass Fluid:
		string get_EOSReference() except +
		string get_TransportReference() except +
		CriticalStruct crit
		OtherParameters params
		FluidLimits limits

		void saturation_p(double p, bool UseLUT, 
				double &TsatLout, double &TsatVout, 
				double &rhoLout, double &rhoVout) except +
		void saturation_T(double T, bool UseLUT, 
				double &psatLout, double &psatVout, 
				double &rhoLout, double &rhoVout) except +

	string get_BibTeXKey(string FluidName, string item) except +
	long get_Fluid_index(string FluidName) except +
	Fluid * get_fluid(long iFluid) except +
	long get_param_index(string param)

cdef extern from "CoolProp/CPState.h":
	cdef cppclass CoolPropStateClassSI:
		CoolPropStateClassSI(string FluidName) except +
		void update(long iInput1, double Value1, 
				long iInput2, double Value2, 
				double T0, double rho0) except +
		double T()
		double rho()
		double p()
		double Q()
		double h()
		double s()
		double cp()
		double cv()
		double speed_sound()
		double isothermal_compressibility()
		double isobaric_expansion_coefficient()
		double dpdT_constrho()
		double dpdrho_constT()
		double dTdp_along_sat()
		double dvdT_constp()
	
		double viscosity()
		double conductivity()
		double Prandtl()
	
		double surface_tension()
		bool TwoPhase
