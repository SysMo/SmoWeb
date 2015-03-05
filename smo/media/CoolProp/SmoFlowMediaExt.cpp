#include "SmoFlowMediaExt.h"
#include <iostream>

void SmoFlow_CoolPropState::createTwoPhaseStates() {
	// Only build the Saturation classes if this is a top-level CPState for which no_SatLSatV() has not been called
	if (!_noSatLSatV){
		if (SatL == NULL){
			SatL = new CoolPropStateClassSI(pFluid);
			SatL->no_SatLSatV(); // Kill the recursive building of the saturation classes
		}
		if (SatV == NULL){
			SatV = new CoolPropStateClassSI(pFluid);
			SatV->no_SatLSatV(); // Kill the recursive building of the saturation classes
		}
	}

}


double SmoFlow_CoolPropState::q() {
	double _q;
	if (TwoPhase) {
		_q = Q();
	} else {
		_q = -1.0;
	}
	return _q;
}

double SmoFlow_CoolPropState::u() {
	return h() - p() / rho();
}

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

double SmoFlow_CoolPropState::dsdT_constq() {
	double _dsdT_constq;
	if (TwoPhase) {
		_dsdT_constq = Q() * dsdT_along_sat_vapor() + (1 - Q()) * dsdT_along_sat_liquid();
	} else {
		_dsdT_constq = NAN;
	}
	return _dsdT_constq;
}

double SmoFlow_CoolPropState::dvdT_constq() {
	double _dvdT_constq;
	if (TwoPhase) {
		double rhoL2 = SatL->rho() * SatL->rho();
		double rhoV2 = SatV->rho() * SatV->rho();
		_dvdT_constq = - Q() / rhoV2 * drhodT_along_sat_vapor() +
						(Q() - 1) / rhoL2 * drhodT_along_sat_liquid();
	} else {
		_dvdT_constq = NAN;
	}
	return _dvdT_constq;
}

double SmoFlow_CoolPropState::dvdq_constT() {
	double _dvdq_constT;
	if (TwoPhase) {
		_dvdq_constT = 1. / SatV->rho() - 1. / SatL->rho();
	} else {
		_dvdq_constT = NAN;
	}
	return _dvdq_constT;
}

double SmoFlow_CoolPropState::dqdT_constv() {
	double _dqdT_constv;
	if (TwoPhase) {
		_dqdT_constv = - dvdT_constq() / dvdq_constT();
	} else {
		_dqdT_constv = NAN;
	}
	return _dqdT_constv;
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

double SmoFlow_CoolPropState::dhdT_constp() {
	double _dhdT_constp;
	if (TwoPhase) {
		_dhdT_constp = INFINITY;
	} else {
		_dhdT_constp = CoolPropStateClassSI::dhdT_constp();
	}
	return _dhdT_constp;
}

double SmoFlow_CoolPropState::dpdT_consth() {
	double _dpdT_consth;
	if (TwoPhase) {
		_dpdT_consth = dpdT_sat();
	} else {
		_dpdT_consth = CoolPropStateClassSI::dpdT_consth();
	}
	return _dpdT_consth;
}

double SmoFlow_CoolPropState::dsdT_constv() {
	double _dsdT_constv;
	if (TwoPhase) {
		_dsdT_constv = dsdq_constT() * dqdT_constv() + dsdT_constq();
	} else {
		_dsdT_constv = CoolPropStateClassSI::dsdT_constrho();
	}
	return _dsdT_constv;
}

