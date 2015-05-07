/*
 * RainflowCounter.cpp
 *
 *  Created on: Apr 23, 2015
 *      Author: Atanas Pavlov
 *      Copyright: SysMo Ltd., Bulgaria
 */

#include "RainflowCounter.h"
#include "core/Definitions.h"

RainflowCounter::RainflowCounter(int numBins)
: numBins(numBins), binCenters(numBins), rainflowMatrix(numBins, numBins),
  residual(numBins) {
}

RainflowCounter::~RainflowCounter() {
}

void RainflowCounter::setStresses(MemoryView1D<double>* sValues) {
	this->sigma = new MemoryView1D<double>(*sValues);
	MemoryView1D<double>& sigma = *(this->sigma);
	this->globalMin = sigma(0);
	this->globalMax = sigma(0);

	// Determine the global minima and maxima
	for (int i = 0; i < sigma.len(); i++) {
		if (sigma(i) < globalMin) {
			globalMin = sigma(i);
		} else if (sigma(i) > globalMax) {
			globalMax = sigma(i);
		}
	}

	// Determine the bin width
	binWidth = (globalMax - globalMin) / (numBins - 1);

	// Determine the bin centers
	for (int i = 0; i < numBins; i++) {
		binCenters[i] = i * binWidth + globalMin;
	}
}

double RainflowCounter::compute() {
	// Compute extrema
	locateExtrema();

	// Compute rainflow matrix
	rainflowMatrix.assign(numBins, numBins, 0);
	computeRainflowMatrix(extremaPercentiles, residual);

	// Treat the residual
	int resLen = residual.size();
	NRvector<int> repeatedResidual (2 * resLen);
	for (int i = 0; i < resLen; i++) {
		repeatedResidual[i] = residual[i];
		repeatedResidual[i + resLen] = residual[i];
	}
	computeRainflowMatrix(repeatedResidual, residual);

	// Compute damage
	computeDamage();
	return damage;
}

void RainflowCounter::locateExtrema() {
	/**
	 * 	This function finds local extrema. It searches for alternating minima and maxima.
	 *	To eliminate noise, a treshold of `binWidth` is used.
	 */
	MemoryView1D<double>& sigma = *(this->sigma);

	// Create the arrays for storing the extrema positions and values
	extremaIndices.resize(sigma.len());
	bool lookingForMaximum;
	int lastMinIndex = 0;
	int lastMaxIndex = 0;
	double lastMinValue = Infinity;
	double lastMaxValue = - Infinity;
	int j = 1;

	// Add the first point
	extremaIndices[0] = 0;

	// Decide if we start searching for min or max
	int i = 1;
	while (fabs(sigma(i) - sigma(0)) < binWidth) {
		i += 1;
	}
	if (sigma(i) > sigma(0)) {
		lookingForMaximum = true;
	} else {
		lookingForMaximum = false;
	}

	// Search in the internal points
	while (i < sigma.len()) {
		double sp = sigma(i);
		// Update the current local max
		if (sp > lastMaxValue) {
			lastMaxValue = sp;
			lastMaxIndex = i;
		}
		// Update the current local min
		if (sp < lastMinValue) {
			lastMinValue = sp;
			lastMinIndex = i;
		}

		if (lookingForMaximum) {
			// If looking for maximum, but have fallen sufficiently below the local one:
			// then declare we have found one
			if (sp < lastMaxValue - binWidth) {
				extremaIndices[j] = lastMaxIndex;
				j += 1;
				lastMinValue = sp;
				lastMinIndex = i;
				lookingForMaximum = false;

			}
		} else {
			// If looking for minimum, but have risen sufficiently above the local one:
			// then declare we have found one
			if (sp > lastMinValue + binWidth) {
				extremaIndices[j] = lastMinIndex;
				j += 1;
				lastMaxValue = sp;
				lastMaxIndex = i;
				lookingForMaximum = true;
			}
		}
		i += 1;
	}

	// Add the last point
	if (extremaIndices[j - 1] != (sigma.len() - 1)) {
		extremaIndices[j] = (sigma.len() - 1);
		j += 1;
	}

	// Trim the index array
//	NRvector<double> tmpExtremaIndices(j);
//	for (int i = 0; i < j; i++) {
//		tmpExtremaIndices[i] = extremaIndices[i];
//	}
//	extremaIndices.resize(j);
	copyResizeVector(extremaIndices, j);
	extremaValues.resize(j);
	extremaPercentiles.resize(j);
	// Take the extrema values and the extrema percentiles
	for (int i = 0; i < j; i++) {
		extremaValues[i] = sigma(extremaIndices[i]);
		extremaPercentiles[i] = floor((extremaValues[i] - globalMin) / binWidth + 0.5);
	}
}

void RainflowCounter::computeRainflowMatrix(NRvector<int>& dataValues, NRvector<int>& residual) {
	residual.assign(numBins, 0);
	int iz = 0;
	int ir = 1;
	int lastRes, secLastRes;
	for (int i = 0; i < dataValues.size(); i++) {
		int s = dataValues[i];
		bool repeat = true;
		while (repeat) {
			repeat = false;
			if (iz > ir) {
				secLastRes = residual[iz - 2];
				lastRes = residual[iz - 1];
				if ((s - lastRes) * (lastRes - secLastRes) >= 0) {
					iz -=  1;
					repeat = true;
				} else if (abs(s - lastRes) >= abs(lastRes - secLastRes)) {
					rainflowMatrix[lastRes][secLastRes] += 1;
					iz = iz - 2;
					repeat = true;
				}
			} else if (iz == ir) {
				lastRes = residual[iz - 1];
				if (((s - lastRes) * lastRes) >= 0) {
					iz -= 1;
					repeat = true;
				} else if (abs(s) > abs(lastRes)) {
					ir += 1;
				}
			}
		}
		residual[iz] = s;
		iz += 1;
	}
	copyResizeVector(residual, iz - 1);
}

void RainflowCounter::setMeanStressCorrection(double M) {
	this->M = M;
}
void RainflowCounter::setSNCurveParameters(double S_E, double N_E, double k) {
	this->S_E = S_E;
	this->N_E = N_E;
	this->k = k;
}

void RainflowCounter::computeDamage() {
	damage = 0;
	for (int i = 0; i < numBins; i++) {
		for (int j = 0; j < numBins; j++) {
			double cycleAmplitude = fabs(binCenters[i] - binCenters[j]) / 2;
			double meanStress = (binCenters[i] + binCenters[j]) / 2;
			double correction;
			if (meanStress >= -cycleAmplitude) {
				correction = M * meanStress;
			} else {
				correction = - M * cycleAmplitude;
			}
			double correctedApmplitude = cycleAmplitude + correction;
			damage += 1 / N_E * pow(correctedApmplitude / S_E, k) * rainflowMatrix[i][j];
		}
	}
}
