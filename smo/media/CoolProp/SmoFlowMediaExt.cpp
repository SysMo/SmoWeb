#include "SmoFlowMediaExt.h"

double SmoFlow_CoolPropState::Pr() {
	double _Pr;
	if (!TwoPhase) {
		_Pr = cp() * viscosity() / conductivity();
	} else {
		double cp2p = interp_linear(_Q, SatL->cp(), SatV->cp());
		_Pr = cp2p * viscosity() / conductivity();
	}
	return _Pr;
}

double SmoFlow_CoolPropState::gamma() {
	double _gamma;
	if (!TwoPhase) {
		_gamma = cp() / cv();
	} else {
		double cp2p = interp_linear(_Q, SatL->cp(), SatV->cp());
		double cv2p = interp_linear(_Q, SatL->cv(), SatV->cv());
		_gamma = cp2p / cv2p;
	}
	return _gamma;
}

double SmoFlow_CoolPropState::beta() {
	double _beta;
	if (!TwoPhase) {
		_beta = _rho * dvdT_constp();
	} else {
		_beta = _rho * interp_linear(_Q, SatL->dvdT_constp(), SatV->dvdT_constp());
	}
	return _beta;
}

double SmoFlow_CoolPropState::dpdrho_constT() {
	double _dpdrho_constT;
	if (TwoPhase) {
		_dpdrho_constT = 0;
	} else {
		_dpdrho_constT = CoolPropStateClassSI::dpdrho_constT();
	}
	return _dpdrho_constT;

}

double SmoFlow_CoolPropState::dsdq_constT() {
	double _dsdq_constT;
	if (TwoPhase) {
		_dsdq_constT = SatV->s() - SatL->s();
	} else {
		_dsdq_constT = NAN;
	}
	return _dsdq_constT;
}

double SmoFlow_CoolPropState::dpdT_sat() {
	return 1./CoolPropStateClassSI::dTdp_along_sat();
}

double SmoFlow_CoolPropState::dpdT_constv() {
	double _dpdT_constv;
	if (TwoPhase) {
		_dpdT_constv = dpdT_sat();
	} else {
		_dpdT_constv = CoolPropStateClassSI::dpdT_constrho();
	}
	return _dpdT_constv;
}

double SmoFlow_CoolPropState::dpdv_constT() {
	double _dpdv_constT;
	if (TwoPhase) {
		_dpdv_constT = 0;
	} else {
		_dpdv_constT = - rho() * rho() * CoolPropStateClassSI::dpdrho_constT();
	}
	return _dpdv_constT;
}

double SmoFlow_CoolPropState::dvdp_constT() {
	double _dvdp_constT;
	if (TwoPhase) {
		_dvdp_constT = INFINITY;
	} else {
		_dvdp_constT = CoolPropStateClassSI::dvdp_constT();
	}
	return _dvdp_constT;
}

double SmoFlow_CoolPropState::dvdT_constp() {
	double _dvdT_constp;
	if (TwoPhase) {
		_dvdT_constp = INFINITY;
	} else {
		_dvdT_constp = CoolPropStateClassSI::dvdT_constp();
	}
	return _dvdT_constp;
}

double SmoFlow_CoolPropState::dsdp_constT() {
	double _dsdp_constT;
	if (TwoPhase) {
		_dsdp_constT = INFINITY;
	} else {
		_dsdp_constT = CoolPropStateClassSI::dsdp_constT();
	}
	return _dsdp_constT;
}
















