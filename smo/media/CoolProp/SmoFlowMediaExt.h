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
	double dsdq_constT();
	double dsdT_constq();
	double dvdT_constq();
	double dvdq_constT();
	double dqdT_constv();
	double dpdT_sat();
	double dpdT_constv();
	double dpdv_constT();
	double dvdp_constT();
	double dvdT_constp();
	double dsdp_constT();
	double dhdT_constp();
	double dpdT_consth();
	double dsdT_constv();

};

#endif // SMOFLOWMEDIAEXT_H
