/*
 * StressTensorCalculator.h
 *
 *  Created on: Apr 25, 2015
 *      Author: nasko
 */

#ifndef STRESSTENSORCALCULATOR_H_
#define STRESSTENSORCALCULATOR_H_

#include "math/ArrayInterface.h"

class StressTensorCalculator {
public:
	StressTensorCalculator();
	virtual ~StressTensorCalculator();

	static void computePrincipalStresses(MemoryView2D<double>* stresses, MemoryView1D<double>* principalStresses);
	static void computePrincipalStresses_Series(MemoryView3D<double>* stressSeries, MemoryView2D<double>* principalStresses);
	static bool checkForZeroStress(MemoryView2D<double>* stresses, double eps = 1e-8);
	static void scaleStressSeries_MultiaxialDamage(MemoryView3D<double>* stressSeries, double k);
};

#endif /* STRESSTENSORCALCULATOR_H_ */
