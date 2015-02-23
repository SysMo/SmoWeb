from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector

cdef extern from "CoolProp/CoolProp.h":
	string get_BibTeXKey(string FluidName, string item) except +
	long get_Fluid_index(string FluidName) except +
	Fluid* get_fluid(long iFluid) except +
	long get_param_index(string param) except +

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
		double Tmin, Tmax, pmax, rhomax

	cdef cppclass EnvironmentalFactorsStruct:
		double GWP20, GWP100, GWP500, ODP, HH, PH, FH
		string ASHRAE34
	
	
	cdef cppclass Fluid:
		string get_EOSReference() except +
		string get_TransportReference() except +
		vector[string] get_aliases() except +
		CriticalStruct crit
		OtherParameters params
		FluidLimits limits
		EnvironmentalFactorsStruct environment

		void saturation_p(double p, bool UseLUT, 
				double &TsatLout, double &TsatVout, 
				double &rhoLout, double &rhoVout) except +
		void saturation_T(double T, bool UseLUT, 
				double &psatLout, double &psatVout, 
				double &rhoLout, double &rhoVout) except +
		


cdef extern from "SmoFlowMediaExt.h":
	cdef cppclass CoolPropStateClassSI:
		double T()
		double rho()
		double p()
		double Q()
		double h()
		double s()
		double cp()
		double cv()
		
	cdef cppclass SmoFlow_CoolPropState:
		SmoFlow_CoolPropState(string FluidName) except +
		SmoFlow_CoolPropState(Fluid *pFluid) except +
		void update(long iInput1, double Value1, 
				long iInput2, double Value2, 
				double T0, double rho0) except +

		double T()
		double rho()
		double p()
		double q()
		double h()
		double s()
		double u()
		double cp()
		double cv()
		double speed_sound()
		double isothermal_compressibility()
		double isobaric_expansion_coefficient()
# 		double dTdp_along_sat()
		double dpdT_sat()
		double gamma()
		double beta()

		double dvdp_constT()
		double dvdT_constp()
	
		double drhodT_constp()
		double drhodp_constT()
# 		double d2rhodp2_constT()
# 		double d2rhodTdp()
# 		double d2rhodT2_constp()
# 		double d2rhodhdQ()
# 		double d2rhodpdQ()
# 		double d2rhodhdp()
# 		double d2rhodh2_constp()
		
		double dpdrho_constT()
		double dpdrho_consth()
		double dpdT_constrho()
		double dpdT_consth()
		double dpdv_constT()
		double dpdT_constv()
# 		double d2pdrho2_constT()
# 		double d2pdrhodT()
# 		double d2pdT2_constrho()
	
		double dhdrho_constT()
		double dhdrho_constp()
		double dhdT_constrho()
		double dhdT_constp()
		double dhdp_constT()
# 		double d2hdrho2_constT()
# 		double d2hdrhodT()
# 		double d2hdT2_constrho()
# 		double d2hdT2_constp()
# 		double d2hdp2_constT()
# 		double d2hdTdp()
	
		double dsdrho_constT()
		double dsdT_constrho()
		double dsdrho_constp()
		double dsdT_constp()
		double dsdp_constT()
		double dsdT_constv()
#		double dsdq_constT()
# 		double d2sdrho2_constT()
# 		double d2sdrhodT()
# 		double d2sdT2_constrho()
# 		double d2sdT2_constp()
# 		double d2sdp2_constT()
# 		double d2sdTdp()

		# Derivatives at saturation
		double drhodT_along_sat_vapor()
		double drhodT_along_sat_liquid()
		double drhodp_along_sat_vapor()
		double drhodp_along_sat_liquid()
		
		double dsdT_along_sat_vapor()
		double dsdT_along_sat_liquid()
		double dsdp_along_sat_vapor()
		double dsdp_along_sat_liquid()

		double dhdp_along_sat_vapor()
		double dhdp_along_sat_liquid()
		double dhdT_along_sat_vapor()
		double dhdT_along_sat_liquid()

		# Two-phase specific derivatives
		double dsdq_constT();
		double dsdT_constq();
		double dvdT_constq();
		double dvdq_constT();
	
		double dqdT_constv();

		#Transport properties
		double viscosity()
		double conductivity()
		double Prandtl()
	
		double surface_tension()
		bool TwoPhase
		CoolPropStateClassSI* getSatL()
		CoolPropStateClassSI* getSatV()
