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
};

#endif // SMOFLOWMEDIAEXT_H
