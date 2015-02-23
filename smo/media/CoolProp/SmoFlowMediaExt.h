/**
 * file: SmoFlowMediaExt.h
 */
#ifndef SMOFLOWMEDIAEXT_H
#define SMOFLOWMEDIAEXT_H

#include "CoolProp/CPState.h"

class SmoFlow_CoolPropState : public CoolPropStateClassSI {
public:
	SmoFlow_CoolPropState(Fluid* pFluid) : CoolPropStateClassSI(pFluid) {}
	SmoFlow_CoolPropState(std::string FluidName) : CoolPropStateClassSI(FluidName) {}

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
	double dsdq_constT();
	double dpdT_sat();
	double dpdT_constv();
	double dpdv_constT();
	double dvdp_constT();
	double dvdT_constp();
	double dsdp_constT();

};

#endif // SMOFLOWMEDIAEXT_H
