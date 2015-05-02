/*
 * StressTensorCalculator.cpp
 *
 *  Created on: Apr 25, 2015
 *      Author: nasko
 */

#include "StressTensorCalculator.h"
#include <math.h>
#include <algorithm>

StressTensorCalculator::StressTensorCalculator() {
	// TODO Auto-generated constructor stub

}

StressTensorCalculator::~StressTensorCalculator() {
	// TODO Auto-generated destructor stub
}

void StressTensorCalculator::computePrincipalStresses(MemoryView2D<double>* stresses, MemoryView1D<double>* principalStresses) {
	/*
	 * http://en.wikiversity.org/wiki/Principal_stresses
	 */
	MemoryView2D<double>& s = *stresses;
	MemoryView1D<double>& ps = *principalStresses;
	// Check if stress tensor is very close to zero
	if (StressTensorCalculator::checkForZeroStress(stresses)) {
		ps(0) = 0; ps(1) = 0; ps(2) = 0;
		return;
	}
	double I1 = s(0, 0) + s(1, 1) + s(2, 2);
	double I2 = s(0, 0) * s(1, 1) + s(1, 1) * s(2, 2) + s(2, 2) * s(0, 0)
		- pow(s(0, 1), 2) - pow(s(1, 2), 2) - pow(s(2, 0), 2);
	double I3 = s(0, 0) * s(1, 1) * s(2, 2)
		- s(0, 0) * pow(s(1, 2), 2) - s(1, 1) * pow(s(2, 0), 2) - s(2, 2) * pow(s(0, 1), 2)
		+ 2 * s(0, 1) * s(1, 2) * s(2, 0);
	double phiArg = (2 * I1 * I1 * I1 - 9 * I1 * I2 + 27 * I3) /
			(2 * pow(I1 * I1 - 3 * I2, 3./2));
	double phi;
	if (phiArg < -1) {
		phi = M_PI / 3;
	} else if (phiArg > 1) {
		phi = 0;
	} else {
		phi = 1./3 * acos(phiArg);
	}
	for (int i = 0; i < 3; i++) {
		ps(i) = 1./3 * I1 + 2./3 * sqrt(I1 * I1 - 3 * I2) * cos(phi + 2./3 * M_PI * i);
	}
	std::sort(ps.begin(), ps.end());
}

void StressTensorCalculator::computePrincipalStresses_Series(MemoryView3D<double>* stressSeries, MemoryView2D<double>* principalStresses) {
	for (int i = 0; i < stressSeries->shape(0); i++) {
		MemoryView2D<double> stress(&(*stressSeries)(i, 0, 0), stressSeries->shape(1), stressSeries->shape(2), stressSeries->strides(1), stressSeries->strides(2));
		MemoryView1D<double> ps(&(*principalStresses)(i, 0), principalStresses->shape(1), principalStresses->strides(1));
		StressTensorCalculator::computePrincipalStresses(&stress, &ps);
	}
}

bool StressTensorCalculator::checkForZeroStress(MemoryView2D<double>* stresses, double eps) {
	for (ssize_t i = 0; i < stresses->shape(0); i++) {
		for (ssize_t j = 0; j < stresses->shape(1); i++) {
			if (fabs((*stresses)(i, j)) > eps) {
				return false;
			}
		}
	}
	return true;
}

void StressTensorCalculator::scaleStressSeries_MultiaxialDamage(MemoryView3D<double>* stressSeries, double k) {
	double principalStresses[3];
	MemoryView1D<double> ps(principalStresses, 3, sizeof(double));
	for (int i = 0; i < stressSeries->shape(0); i++) {
		MemoryView2D<double> stress(&(*stressSeries)(i, 0, 0), stressSeries->shape(1), stressSeries->shape(2), stressSeries->strides(1), stressSeries->strides(2));
		StressTensorCalculator::computePrincipalStresses(&stress, &ps);
		double V = 1.0;
		// Take the ratio of min/max stress
		// V = -1: dominating shear stress
		// V = 0: dominating tension/copression stress
		// V = 1: hydro-static pressure

		// Scale coefficient
		double f;

		if (fabs(ps(0)) > fabs(ps(2)) && fabs(ps(0)) > 1e-8) {
			V = ps(2) / ps(0);
			f = 1. + (1. - k) * V;
		} else if (fabs(ps(2)) > 1e-8){
			V = ps(0) / ps(2);
			f = 1. + (1. - k) * V;
		} else {
			f = 1.;
		}
		//ShowMessage("Scaling by f =" << f)
		for (int i = 0; i < 3; i++) {
			for (int j = 0; j < 3; j++) {
				stress(i, j) *= f;
			}
		}
	}
}
