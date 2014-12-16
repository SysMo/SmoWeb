#include "SmoFlowMediaExt.h"

double SmoFlow_CoolPropState::Pr() {
	if (!TwoPhase) {
		return cp() * viscosity() / conductivity();
	} else {
		double cp2p = interp_linear(_Q, SatL->cp(), SatV->cp());
		return cp2p * viscosity() / conductivity();
	}
}

double SmoFlow_CoolPropState::gamma() {
	if (!TwoPhase) {
		return cp() / cv();
	} else {
		double cp2p = interp_linear(_Q, SatL->cp(), SatV->cp());
		double cv2p = interp_linear(_Q, SatL->cv(), SatV->cv());
		return cp2p / cv2p;
	}
}

double SmoFlow_CoolPropState::beta() {
	if (!TwoPhase) {
		return _rho * dvdT_constp();
	} else {
		return _rho * interp_linear(_Q, SatL->dvdT_constp(), SatV->dvdT_constp());
	}
}
