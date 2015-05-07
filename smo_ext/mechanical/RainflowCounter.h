/*
 * RainflowCounter.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Atanas Pavlov
 *      Copyright: SysMo Ltd., Bulgaria
 */

#ifndef RAINFLOWCALCULATOR_H_
#define RAINFLOWCALCULATOR_H_

#include "core/Definitions.h"
#include "math/ArrayInterface.h"
#include "math/VectorsMatrices.h"

class RainflowCounter {
public:
	RainflowCounter(int numBins);
	virtual ~RainflowCounter();

	void setStresses(MemoryView1D<double>* sValues);
	void setMeanStressCorrection(double M);
	void setSNCurveParameters(double S_E, double N_E, double k);
	double compute();

protected:
	void locateExtrema();
	void computeRainflowMatrix(NRvector<int>& dataValues, NRvector<int>& residual);
	void residualRepeateRun(NRvector<int>& residual);
	void computeDamage();
protected:
	int numBins;
	MemoryView1D<double>* sigma;
	double globalMin;
	double globalMax;
	double binWidth;
	NRvector<double> binCenters;

	NRvector<int> extremaIndices;
	NRvector<double> extremaValues;
	NRvector<int> extremaPercentiles;

	NRmatrix<int> rainflowMatrix;
	NRvector<int> residual;

	NRmatrix<double> cycleAmplitudes;
	NRmatrix<double> meanStresses;

	double S_E;
	double N_E;
	double k;
	double M;

	double damage;
};

#endif /* RAINFLOWCALCULATOR_H_ */
