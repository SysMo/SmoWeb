/**
 * file: SmoFlowMediaExt.h
 */
#ifndef SMOFLOWMEDIAEXT_H
#define SMOFLOWMEDIAEXT_H

#include "CoolProp/CPState.h"

class SmoFlow_CoolPropState : public CoolPropStateClassSI {
public:
	SmoFlow_CoolPropState(Fluid* pFluid) : CoolPropStateClassSI(pFluid) {
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
	SmoFlow_CoolPropState(std::string FluidName) : CoolPropStateClassSI(FluidName) {}

	double q();
	double u();
	double Pr();
	double gamma();
	double beta();

	CoolPropStateClassSI* getSatL() {
		return SatL;
	}
	CoolPropStateClassSI* getSatV() {
		return SatV;
	}

	// Derivatives
	double dpdrho_constT();
	double dpdT_constv();
	double dpdv_constT();
	double dvdp_constT();
	double dvdT_constp();
	double dhdT_constp();
	double dpdT_consth();
	double dsdT_constv();
	double dsdp_constT();

	// Two-phase specific derivatives
	double dsdq_constT();
	double dsdT_constq();
	double dvdT_constq();
	double dvdq_constT();

	double dqdT_constv();

	// Derivatives at saturation
	double dpdT_sat();
};

#endif // SMOFLOWMEDIAEXT_H
