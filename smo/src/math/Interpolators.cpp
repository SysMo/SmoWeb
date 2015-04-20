/*
 * Interpolators.cpp
 *
 *  Created on: Aug 7, 2013
 *      Author: Atanas Pavlov
 *	 Copyright: SysMo Ltd., Bulgaria
 */

#include "Interpolators.h"

Interpolator1D::Interpolator1D(VectorD& xValues, VectorD& yValues, size_t interpolationOrder,
		bool copyValues, InterpolationBoundaryHandling boundaryHandling)
:interpolationOrder(interpolationOrder), boundaryHandling(boundaryHandling) {
	this->keepValues = copyValues;
	numValues = xValues.size();
	if (copyValues) {
		this->xValues = new double[numValues];
		this->yValues = new double[numValues];
		for (int i = 0; i < numValues; i++) {
			this->xValues[i] = xValues[i];
			this->yValues[i] = yValues[i];
		}
	} else {
		this->xValues = &xValues[0];
		this->yValues = &yValues[0];
	}
}

Interpolator1D::Interpolator1D(double* xValues, double* yValues, int numValues, size_t interpolationOrder,
		bool copyValues, InterpolationBoundaryHandling boundaryHandling)
:interpolationOrder(interpolationOrder), boundaryHandling(boundaryHandling) {
	this->keepValues = copyValues;
	this->numValues = numValues;
	if (copyValues) {
		this->xValues = new double[numValues];
		this->yValues = new double[numValues];
		for (int i = 0; i < numValues; i++) {
			this->xValues[i] = xValues[i];
			this->yValues[i] = yValues[i];
		}
	} else {
		this->xValues = &xValues[0];
		this->yValues = &yValues[0];
	}
}

Interpolator1D::~Interpolator1D() {
	if (keepValues) {
		delete[] xValues;
		delete[] yValues;
	}
}

size_t Interpolator1D::hunt(double xValue) {
	size_t jm, ju, inc = 1;
	size_t jl = 0;
	if (numValues < 2 || interpolationOrder < 2 || interpolationOrder > numValues)
		throw("hunt size error");

	if (jl < 0 || jl > numValues - 1) {
		jl = 0;
		ju = numValues - 1;
	} else {
		if (xValue >= xValues[jl]) {
			for (;;) {
				ju = jl + inc;
				if (ju >= numValues - 1) {
					ju = numValues - 1;
					break;
				} else if (xValue < xValues[ju])
					break;
				else {
					jl = ju;
					inc += inc;
				}
			}
		} else {
			ju = jl;
			for (;;) {
				jl = jl - inc;
				if (jl <= 0) {
					jl = 0;
					break;
				} else if (xValue >= xValues[jl])
					break;
				else {
					ju = jl;
					inc += inc;
				}
			}
		}
	}
	while (ju - jl > 1) {
		jm = (ju + jl) >> 1;
		if (xValue >= xValues[jm])
			jl = jm;
		else
			ju = jm;
	}
	return Max(0., Min(numValues - interpolationOrder, jl - ((interpolationOrder - 2) >> 1)));
}

double Interpolator1D::operator()(double value) {
	if (isNaN(value)) {
		RaiseError("Not-a-number value passesd to interpolator");
	}
	double yValue;
	if (boundaryHandling == ibhConstant && value < xValues[0]) {
		yValue = yValues[0];
	} else if (boundaryHandling == ibhConstant && value > xValues[numValues - 1]) {
		yValue = yValues[numValues - 1];
	} else {
		size_t i = hunt(value);
		yValue = rawInterp(i, value);
	}
	return yValue;
}


double LinearInterpolator::rawInterp(size_t xIndex, double xValue) {
	if (xValues[xIndex] == xValues[xIndex + 1])
		return yValues[xIndex];
	else
		return yValues[xIndex] + ((xValue - xValues[xIndex])
				/ (xValues[xIndex + 1] - xValues[xIndex]))
				* (yValues[xIndex + 1] - yValues[xIndex]);

}

